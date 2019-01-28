from Parser.Utils import *
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

URL_JOHNLEWIS_HOME = "https://www.johnlewis.com/"


def get_categories() -> pd.DataFrame:
    raw_html = simple_get(URL_JOHNLEWIS_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.find_all(name="a")
    output = []
    for result in results:
        root_node = ET.fromstring(str(result))
        if "href" in root_node.attrib and \
                (root_node.attrib["href"].startswith("/browse/men/") or \
                 root_node.attrib["href"].startswith("/browse/women/") or \
                 root_node.attrib["href"].startswith("/browse/baby-child/")):
            url = root_node.attrib["href"]
            taxonomy = url.split("/")
            taxonomy = [x for x in taxonomy if x != "_"]
            output.append({"taxo1": taxonomy[2],
                           "taxo2": (taxonomy[3] if len(taxonomy) > 3 else None),
                           "taxo3": (taxonomy[4] if len(taxonomy) > 4 else None),
                           "URL": URL_JOHNLEWIS_HOME + url})
    output_df = pd.DataFrame(output)
    output_df = output_df.drop_duplicates()
    return output_df


def get_page_inventory(taxonomy: [str], last_level: str, url: str) -> pd.DataFrame:
    try:
        print('suburl: {}'.format(url))
        taxonomy = taxonomy.copy()
        taxonomy.append(last_level)

        i = None
        products = []
        while True:
            if i is None:
                url_prod = url
                i = 1
            else:
                i += 8
                url_prod = url + "?page={}".format(i)
            i = i + 1
            raw_html = simple_get(url_prod)
            html = BeautifulSoup(raw_html, 'html.parser')

            # get highlighted products
            spotlight_node = html.findAll(name="section", attrs={"class": "product-card"})
            if len(spotlight_node) == 0 or i > 200:
                break
            for node in spotlight_node:
                try:
                    data = ET.fromstring(str(node))
                    name = data[1][0][0][0].text
                    price = None

                    url_product = URL_JOHNLEWIS_HOME + data[1][0].attrib["href"]
                    product_id = data.attrib["data-product-id"]

                    for subnode in data.findall('./*/*/*/'):
                        if "class" in subnode.attrib and \
                                subnode.attrib["class"].startswith('product-card__price'):
                            new_price = re.search('.([0-9.]+\.?[0-9]*)', subnode.text, re.IGNORECASE).group(1)
                            price = float(new_price) if price is None or \
                                                        (price is not None and price > float(new_price)) else price
                    products.append(add_in_dictionary(shop=Shop.JOHNLEWIS,
                                                      obj_id=product_id,
                                                      reference=None,
                                                      name=name,
                                                      price=price,
                                                      in_stock=True,
                                                      taxo1=taxonomy[0] if len(taxonomy) >= 1 else None,
                                                      taxo2=taxonomy[1] if len(taxonomy) >= 2 else None,
                                                      taxo3=taxonomy[2] if len(taxonomy) >= 3 else None,
                                                      taxo4=taxonomy[3] if len(taxonomy) >= 4 else None,
                                                      url=url_product))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR,
                              shop=Shop.JOHNLEWIS, message="Error spotlight page {} : {} ({})".format(i, node, ex),
                              url=url)

        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.JOHNLEWIS, message=str(ex), url=url)
    return None


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    try:
        print("url: {}".format(url))
        output = []

        taxonomy = [taxo1, taxo2, taxo3]
        taxonomy = [x for x in taxonomy if x is not None]
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')
        filters = html.findAll(name="div", attrs={"class": "faceted-filters-accordion"})

        try:
            for product_filter in filters:
                data = ET.fromstring(str(product_filter))
                if data[0].text.strip() == 'Product Type':
                    for subnode in data[1][0]:
                        name = subnode[0].text.strip()
                        output.append(get_page_inventory(taxonomy=taxonomy,
                                                         last_level=name,
                                                         url=URL_JOHNLEWIS_HOME + subnode[0].attrib["href"]))
        except Exception as ex:
            log_error(level=ErrorLevel.MINOR, shop=Shop.JOHNLEWIS, message=str(ex), url=url)

        if len(output) == 0:
            output.append(get_page_inventory(taxonomy=taxonomy,
                                             last_level=None,
                                             url=url))

        return pd.concat(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.JOHNLEWIS, message=str(ex), url=url)
    return None


def parse_john_lewis():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.JOHNLEWIS, message=str(ex))
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.JOHNLEWIS, message=str(ex))
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.JOHNLEWIS, df=df)
