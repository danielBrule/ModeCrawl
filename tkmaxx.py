from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
import re
from bs4 import BeautifulSoup

URL_TKMAXX_HOME = "https://www.tkmaxx.com/uk/en/sitemap.xml"


def get_categories() -> pd.DataFrame:
    sitemap_xml = simple_get(URL_TKMAXX_HOME)
    sitemap_root_node = ET.fromstring(sitemap_xml)

    sitemap_url = []
    for href in sitemap_root_node:
        sitemap_url.append(href[0].text)

    sitemap_url = [x for x in sitemap_url if "Category-en" in x]

    sitemap_product_url = []
    for products in sitemap_url:
        sitemap_category_xml = simple_get(products)
        sitemap_category_root_node = ET.fromstring(sitemap_category_xml)
        for category in sitemap_category_root_node:
            sitemap_product_url.append(category[0].text)

    sitemap_product_url = [x for x in sitemap_product_url if "men" in x or "women" in x or "kids" in x]

    output = []
    for url in sitemap_product_url:
        taxonomy = url.replace('https://www.tkmaxx.com/uk/en/', '')
        taxonomy = re.sub(r"/c/[0-9]+", "", taxonomy)
        taxonomy = taxonomy.split("/")
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "URL": url})
    output = pd.DataFrame(output)
    return output


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("url: {}".format(url))
    try:

        products = []
        i = 0
        while True:
            raw_html = simple_get(url)
            html = BeautifulSoup(raw_html, 'html.parser')

            if "The page you were looking for does not exist" in html:
                return None

            data = simple_get(
                url + "/autoLoad?q=&page={}".format(i))
            # url + "/autoLoad?q=&sort=publishedDate-desc&facets=stockLevelStatus%3AinStock&fetchAll=true&page=0")
            data = json.loads(data)

            number_of_pages = data['pagination']['numberOfPages']
            for node in data["results"]:
                try:
                    products.append(add_in_dictionary(shop=Shop.TKMAXX,
                                                      obj_id=node['code'],
                                                      reference=None,
                                                      name=node['label'],
                                                      price=node['price']['value'],
                                                      in_stock=True if node['stockLevelStatus'] == "inStock"
                                                      else False,
                                                      taxo1=taxo1,
                                                      taxo2=taxo2,
                                                      taxo3=taxo3,
                                                      url="https://www.tkmaxx.com/uk/" + node['url']))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.NEWLOOK, message=ex)
            i += 1
            if i >= number_of_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.TKMAXX, message=ex)
    return None


def parse_tkmaxx():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.TKMAXX, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.TKMAXX, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.TKMAXX, df=df)

