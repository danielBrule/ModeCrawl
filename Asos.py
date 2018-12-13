from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
import re

URL_ASOS_HOME_MEN = "https://www.asos.com/sitemap.xml?site=en-GB&categoryId=1001&categoryName=Men"
URL_ASOS_HOME_WOMEN = "https://www.asos.com/sitemap.xml?site=en-GB&categoryId=1000&categoryName=Women"


def get_categories(url: str) -> pd.DataFrame:
    raw_xml = simple_get(url, USER_AGENT)
    root_node = ET.fromstring(raw_xml)

    href_list = []
    for href in root_node:
        href_list.append(href[0].text)

    href_list = [x for x in href_list if "a-to-z-of-brands" not in x]

    output = []
    for i in range(0, len(href_list[:-1])):
        element_1 = href_list[i][:-5]
        element_2 = href_list[i + 1]
        if not element_2.startswith(element_1):
            element_1 = element_1.replace('https://www.asos.com/', '')
            element_1 = element_1.split("/")
            output.append({"taxo1": element_1[0],
                           "taxo2": element_1[1],
                           "taxo3": (element_1[2] if len(element_1) > 2 and element_1[2] != "cat" else None),
                           "URL": href_list[i]})
    output = pd.DataFrame(output)
    return output


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("{} - Category: {}".format(Shop.ASOS.name, url))
    try:
        find = re.search('cat/\?cid=([0-9]+)', url, re.IGNORECASE)

        if find is None:
            print("error no cid with URL {}".format(url))
            return None
        cid = find.group(1)
        json_url = \
            "https://api.asos.com/product/search/v1/categories/{}?channel=mobile-web&country=GB" \
            "&currency=GBP&keyStoreDataversion=fcnu4gt-12&lang=en&limit=5000&offset=0&rowlength=2&store=1".format(cid)
        data = simple_get(json_url, USER_AGENT)
        data = json.loads(data)

        products = []
        for node in data["products"]:
            try:
                products.append(add_in_dictionary(shop=Shop.ASOS,
                                                  obj_id=node["id"],
                                                  reference=node["productCode"],
                                                  name=node["title"] if "title" in node else node["name"],
                                                  price=node["price"]["current"]["value"],
                                                  in_stock=True,
                                                  taxo1=taxo1,
                                                  taxo2=taxo2,
                                                  taxo3=taxo3,
                                                  url="https://www.asos.com/" + node["url"]))
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.ASOS, message=ex)
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ASOS, message=ex)
    return None


def parse_asos():
    # get url to analyse
    try:
        df_url = get_categories(URL_ASOS_HOME_MEN)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.ASOS, message=ex)
        return
    df_url = pd.concat([df_url, get_categories(URL_ASOS_HOME_WOMEN)])

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.ASOS, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.ASOS, df=df)

