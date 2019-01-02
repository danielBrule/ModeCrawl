from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup

URL_TKMAXX_HOME = "https://www.gap.co.uk/sitemap_2-category.xml"
BASE_URL = "https://www.gap.co.uk/on/demandware.store/Sites-ShopUK-Site/en_GB/Product-LazyLoadBatchTiles?pids=%5B%"
BASE_URL_END = "5D&cgid=1110339&ulid=1110339"


def get_categories() -> pd.DataFrame:
    sitemap_product_url = []
    sitemap_category_xml = simple_get(URL_TKMAXX_HOME)
    sitemap_category_root_node = ET.fromstring(sitemap_category_xml)
    for category in sitemap_category_root_node:
        sitemap_product_url.append(category[0].text)

    sitemap_product_url = [x for x in sitemap_product_url if "gap/men" in x or "gap/women" in x or "gap/boys" in x
                           or "gap/girls" in x]
    output = []
    for url in sitemap_product_url:
        taxonomy = url.replace('https://www.gap.co.uk/', '')
        taxonomy = taxonomy.split("/")
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "URL": url})
    output = pd.DataFrame(output)
    return output


def parse_json(taxo1: str, taxo2: str, taxo3: str, output: [], url: str) -> []:
    data = simple_get(url)
    data = json.loads(data)
    for node in data["productHits"]:
        try:
            output.append(add_in_dictionary(shop=Shop.GAP,
                                            obj_id=node['id'],
                                            reference=node['uuid'],
                                            name=node['name'],
                                            price=node['prices'][0]['value'][1:],
                                            in_stock=True,
                                            taxo1=taxo1,
                                            taxo2=taxo2,
                                            taxo3=taxo3,
                                            url=None))
        except Exception as ex:
            log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="PARSE JSON {}: {}".format(url, ex))
    return output


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("url: {}".format(url))
    try:
        products = []
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        product_node = html.findAll(name="div", attrs={"class": "sds_g-inner sds_grid-inner "})
        for node in product_node:
            try:
                products.append(node["data-loopproducthit"])
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="HTML parsing: {}".format(ex))

        url = BASE_URL
        i = 0
        output = []
        for product in products:
            url = url + "22" + product + "%22%2C%"
            i += 1
            if i % 40 == 0:
                url = url[:-3] + BASE_URL_END
                try:
                    output = parse_json(taxo1=taxo1, taxo2=taxo2, taxo3=taxo3, output=output, url=url)
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="LOAD JSON: {}".format(ex))

        if i % 40 != 0:
            url = url[:-3] + BASE_URL_END
            try:
                output = parse_json(taxo1=taxo1, taxo2=taxo2, taxo3=taxo3, output=output, url=url)
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="LOAD JSON: {}".format(ex))

        return pd.DataFrame(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.GAP, message=ex)
    return None


def parse_gap():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.GAP, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.GAP, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.GAP, df=df)
