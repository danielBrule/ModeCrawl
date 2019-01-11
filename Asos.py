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
            log_error(level=ErrorLevel.MEDIUM, shop=Shop.ASOS, message="error no cid with URL {}".format(url))
            return None
        cid = find.group(1)
        offset = 0
        products = []
        while True:
            offset = len(products)
            json_url = \
                "https://api.asos.com/product/search/v1/categories/{}?channel=mobile-web&country=GB" \
                "&currency=GBP&keyStoreDataversion=fcnu4gt-12&lang=en&limit=5000&offset={}&" \
                "rowlength=2&store=1".format(cid, offset)
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
                                                      taxo1=taxo1,
                                                      taxo2=taxo2,
                                                      taxo3=taxo3,
                                                      url="https://www.asos.com/" + node["url"]))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.ASOS, message=ex)
            if len(products) >= nb_items:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ASOS, message=ex)
    return None


def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    df["is_subcat"] = df.apply(lambda my_row:
                               False
                               if "accessories" in my_row["taxo2"].lower() or
                                  "coats-jackets" in my_row["taxo2"].lower() or
                                  "dresses" in my_row["taxo2"].lower() or
                                  "hoodies-sweatshirts" in my_row["taxo2"].lower() or
                                  "jackets-coats" in my_row["taxo2"].lower() or
                                  "jeans" in my_row["taxo2"].lower() or
                                  "jumpers-cardigans" in my_row["taxo2"].lower() or
                                  "jumpsuits-playsuits" in my_row["taxo2"].lower() or
                                  "lingerie-nightwear" in my_row["taxo2"].lower() or
                                  "polo-shirts" in my_row["taxo2"].lower() or
                                  "shirts" in my_row["taxo2"].lower() or
                                  "shoes" in my_row["taxo2"].lower() or
                                  "shoes-boots-trainers" in my_row["taxo2"].lower() or
                                  "shorts" in my_row["taxo2"].lower() or
                                  "skirts" in my_row["taxo2"].lower() or
                                  "socks-tights" in my_row["taxo2"].lower() or
                                  "suits" in my_row["taxo2"].lower() or
                                  "suits-separates" in my_row["taxo2"].lower() or
                                  "swimwear-beachwear" in my_row["taxo2"].lower() or
                                  "tops" in my_row["taxo2"].lower() or
                                  "tracksuits" in my_row["taxo2"].lower() or
                                  "trousers-chinos" in my_row["taxo2"].lower() or
                                  "trousers-leggings" in my_row["taxo2"].lower() or
                                  "t-shirts-vests" in my_row["taxo2"].lower() or
                                  "underwear-socks" in my_row["taxo2"].lower() or
                                  "vests" in my_row["taxo2"].lower()
                               else True, axis=1)

    #######################
    df_url_is_subcat = df.loc[df['is_subcat'] == True].copy()
    df_url_is_subcat = df_url_is_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])

    df_url_is_subcat["is_ctas"] = df_url_is_subcat.apply(lambda my_row:
                                                         True
                                                         if "ctas" in my_row["taxo2"].lower()
                                                         else False, axis=1)
    df_url_is_subcat_ctas = df_url_is_subcat.loc[df_url_is_subcat['is_ctas'] == True].copy()
    df_url_is_subcat_ctas = df_url_is_subcat_ctas.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_subcat_ctas = df_url_is_subcat_ctas.drop(["is_subcat", "is_ctas"], axis=1)

    df_url_is_not_subcat_ctas = df_url_is_subcat.loc[df_url_is_subcat['is_ctas'] == False].copy()
    df_url_is_not_subcat_ctas = df_url_is_not_subcat_ctas.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_not_subcat_ctas = df_url_is_not_subcat_ctas.drop(["is_subcat", "is_ctas"], axis=1)

    #######################
    df_url_is_not_subcat = df.loc[df['is_subcat'] == False].copy()
    df_url_is_not_subcat = df_url_is_not_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_not_subcat = df_url_is_not_subcat.drop(["is_subcat"], axis=1)

    df = pd.concat([df_url_is_not_subcat, df_url_is_not_subcat_ctas, df_url_is_subcat_ctas], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df


def parse_asos():
    # get url to analyse
    try:
        df_url_men = get_categories(URL_ASOS_HOME_MEN)
        df_url_women = get_categories(URL_ASOS_HOME_WOMEN)
        df_url = pd.concat([df_url_men, df_url_women])
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.ASOS, message=ex)
        return

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
    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.ASOS, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.ASOS, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.ASOS, message=ex)
        return
