from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import re

URL_ASOS_HOME_PAGE = "https://www.asos.com"

URL_ASOS_HOME_MEN = "https://www.asos.com/sitemap.xml?site=en-GB&categoryId=1001&categoryName=Men"
URL_ASOS_HOME_WOMEN = "https://www.asos.com/sitemap.xml?site=en-GB&categoryId=1000&categoryName=Women"


def get_categories() -> pd.DataFrame:
    raw_html = simple_get(URL_ASOS_HOME_PAGE, USER_AGENT)
    html = BeautifulSoup(raw_html, 'html.parser')
    menu_iter = html.find_all(name="section")
    output = []

    for submenu in menu_iter:
        root_node = ET.fromstring(str(submenu))
        if not ("class" in root_node.attrib and root_node.attrib["class"].startswith("_1QmxDO_")):
            continue

        category_name = root_node.findall(".//span[@class='_2HjZSOc']")
        if len(category_name) == 0 or "PRODUCT" not in category_name[0].text:
            continue
        urls = root_node.findall(".//a[@class='_2Aejr0d']")
        for url in urls:
            if url.text == "View all" or url.text == "Face + Body" or url.text == "New in" or \
                    url.text == "Back in stock" or \
                    url.text == "Body care" or \
                    url.text == "Fragrances" or \
                    url.text == "Hair care" or \
                    url.text == "Makeup" or \
                    url.text == "Shaving & Beard" or \
                    url.text == "Skin care" or \
                    url.text == "Living + Gifts" or \
                    url.text == "Bestsellers" or \
                    url.text == "Gifts" or \
                    url.text == "New in: Clothing" or \
                    url.text == "New in: Shoes & Accessories" or \
                    url.text == "Trending now":
                continue
            url_short = url.attrib["href"].split("&")[0]
            taxo = url_short.replace('https://www.asos.com/', '')
            taxo = taxo.split("/")
            output.append({"taxo1": taxo[0],
                           "taxo2": taxo[1],
                           "taxo3": url.text,
                           "URL": url_short})
    output = pd.DataFrame(output)
    return output


def get_page_inventory(taxonomy: [str], last_level: str, cid: str, subcid: str) -> pd.DataFrame:
    try:
        print('suburl: {} '.format(last_level))
        taxonomy = taxonomy.copy()
        if last_level is not None:
            taxonomy.append(last_level)
        products = []
        while True:
            offset = len(products)
            if subcid is None:
                json_url = \
                    "https://api.asos.com/product/search/v1/categories/{}?channel=mobile-web&country=GB" \
                    "&currency=GBP&keyStoreDataversion=fcnu4gt-12&lang=en&limit=5000&offset={}&" \
                    "rowlength=2&store=1".format(cid, offset)
            else:
                json_url = \
                    "https://api.asos.com/product/search/v1/categories/{}?channel=mobile-web&country=GB" \
                    "&currency=GBP&keyStoreDataversion=fcnu4gt-12&lang=en&limit=5000&offset={}&" \
                    "rowlength=2&store=1&refine=attribute_1047:{}".format(cid, offset, subcid)
            data = simple_get(json_url, USER_AGENT)
            data = json.loads(data)
            nb_items = data["itemCount"]
            if len(data["products"]) == 0:
                break
            for node in data["products"]:
                try:
                    products.append(add_in_dictionary(shop=Shop.ASOS,
                                                      obj_id=node["id"],
                                                      reference=node["productCode"],
                                                      name=node["title"] if "title" in node else node["name"],
                                                      price=node["price"]["current"]["value"],
                                                      in_stock=True,
                                                      taxo1=taxonomy[0] if len(taxonomy) >= 1 else None,
                                                      taxo2=taxonomy[1] if len(taxonomy) >= 2 else None,
                                                      taxo3=taxonomy[2] if len(taxonomy) >= 3 else None,
                                                      taxo4=taxonomy[3] if len(taxonomy) >= 4 else None,
                                                      url="https://www.asos.com/" + node["url"]))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.ASOS, message=str(ex), url=subcid)
            if len(products) >= nb_items:
                break
        df = pd.DataFrame(products)
        print('suburl: {} - {}'.format(last_level, len(df)))
        return df
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ASOS, message=str(ex), url=subcid)
    return None


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str) -> pd.DataFrame:
    print("{} - Category: {}".format(Shop.ASOS.name, url))
    try:
        find = re.search('cat/\?cid=([0-9]+)', url, re.IGNORECASE)
        cid = find.group(1)

        taxonomy = [taxo1, taxo2, taxo3]
        taxonomy = [x for x in taxonomy if x is not None]

        output = []

        raw_html = simple_get(url, USER_AGENT)
        html = BeautifulSoup(raw_html, 'html.parser')
        category_iter = html.find_all(name="div", attrs={"class": "bybwbES"})
        for category in category_iter:
            try:
                root_node = ET.fromstring(str(category))
                filter_name = root_node.findall(".//div[@class='_3lFxFJi']")
                if len(filter_name) == 0 or "Product Type" != filter_name[0].text:
                    continue
                filters_iter = root_node.findall(".//div[@class='_2h_c2tR']")
                for filter_elem in filters_iter:
                    sub_cid = filter_elem[0].attrib["value"]
                    last_level = filter_elem[1].text.strip()
                    output.append(
                        get_page_inventory(taxonomy=taxonomy, last_level=last_level, cid=cid, subcid=sub_cid))
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.ASOS, message=str(ex), url=url)
        if len(output) == 0:
            return get_page_inventory(taxonomy=taxonomy, last_level=None, cid=cid, subcid=None)
        return pd.concat(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ASOS, message=str(ex), url=url)
    return None


def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    df["taxo3"] = df["taxo3"].apply(str)

    conditions_1 = {"taxo2":
                        {"operator": Comparison.IN,
                         "value": ["accessories", "coats-jackets", "dresses", "hoodies-sweatshirts", "jackets-coats",
                                   "jeans", "jumpers-cardigans", "jumpsuits-playsuits", "lingerie-nightwear",
                                   "polo-shirts", "shirts", "shoes", "shoes-boots-trainers", "shorts", "skirts",
                                   "socks-tights", "suits", "suits-separates", "swimwear-beachwear", "tops",
                                   "tracksuits", "trousers-chinos", "trousers-leggings", "t-shirts-vests",
                                   "underwear-socks", "vests", "goingout", "petite", "tall"]
                         }}

    output = split_and_sort(df=df, true_first=True, conditions=conditions_1)
    df_1 = output[0]
    df_2 = output[1]

    conditions_2 = {"taxo2":
                        {"operator": Comparison.IN,
                         "value": ["ctas", "living-gifts", "outlet", "sale"]
                         },
                    "taxo3":
                        {"operator": Comparison.IN,
                         "value": ["ctas", "None"]
                         }
                    }
    output = split_and_sort(df=df_2, true_first=False, conditions=conditions_2)
    df_2 = output[0]
    df_3 = output[1]
    conditions_3 = {"taxo2":
                        {"operator": Comparison.IN,
                         "value": ["ctas"]
                         },
                    "taxo3":
                        {"operator": Comparison.IN,
                         "value": ["ctas"]
                         }
                    }
    output = split_and_sort(df=df_3, true_first=False, conditions=conditions_3)
    df_3 = output[0]
    df_4 = output[1]

    df = pd.concat([df_1, df_2, df_3, df_4], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df


def parse_asos():
    # get url to analyse
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.ASOS, message=str(ex))
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.ASOS, message=str(ex))
        return

    df = pd.concat(df_list)
    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.ASOS, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.ASOS, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.ASOS, message=str(ex))
        return
