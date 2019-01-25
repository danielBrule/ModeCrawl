from Parser.Utils import *
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

URL_MS_HOME = "https://www.marksandspencer.com"

# TODO improve get sub categorues

def get_categories() -> pd.DataFrame:
    raw_html = simple_get(URL_MS_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')
    output = []

    results = html.find_all(name="a")
    output = []
    for result in results:
        root_node = ET.fromstring(str(result))
        if "href" in root_node.attrib and \
                (root_node.attrib["href"].startswith("/l/men/") or
                 root_node.attrib["href"].startswith("/l/women/") or
                 root_node.attrib["href"].startswith("/l/kids/") or
                 root_node.attrib["href"].startswith("/l/lingerie/")) and \
                "new-in" not in root_node.attrib["href"]:
            url = root_node.attrib["href"].split("?")[0]
            taxonomy = url.split("/")
            output.append({"taxo1": taxonomy[2],
                           "taxo2": (taxonomy[3] if len(taxonomy) > 3 else None),
                           "taxo3": (taxonomy[4] if len(taxonomy) > 4 else None),
                           "URL": URL_MS_HOME + url})
    output_df = pd.DataFrame(output)
    output_df = output_df.drop_duplicates()
    return output_df


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("url: {}".format(url))
    i = 1
    products = []
    try:
        while True:
            url_prod = url + "?pageChoice={}".format(i)
            raw_html = simple_get(url_prod)
            html = BeautifulSoup(raw_html, 'html.parser')

            # get number of page
            nb_pages = html.findAll(name="span", attrs={"class": "pagination__page-x-of-y"})
            nb_pages = str(nb_pages[0].contents[1])
            nb_pages = int(re.search('[0-9]+ of ([0-9]+)', nb_pages, re.IGNORECASE).group(1))

            # get highlighted products
            spotlight_node = html.findAll(name="a", attrs={"class": "spotlight__link"})
            for node in spotlight_node:
                try:
                    data = ET.fromstring(str(node))
                    name = ""
                    price = ""

                    url_product = "https://www.marksandspencer.com" + data.attrib["href"]
                    product_id = re.search('/p/([a-zA-Z0-9]+)?', url_product, re.IGNORECASE).group(1)
                    for subnode in data.findall('./*/*/'):
                        if subnode.attrib["class"] == "spotlight__title":
                            name = subnode.text
                        if subnode.attrib["class"] == "spotlight__normalPrice":
                            price = re.search('.([0-9.]+)', subnode.text, re.IGNORECASE).group(1)
                    products.append({"shop": Shop.MS,
                                     "id": product_id,
                                     "reference": None,
                                     "name": name,
                                     "price": price,
                                     "inStock": True,
                                     "taxo1": taxo1,
                                     "taxo2": taxo2,
                                     "taxo3": taxo3,
                                     "url": url_product,
                                     "date": datetime.datetime.now()})
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR,
                              shop=Shop.MS, message="Error spotlight page {} : {} ({})".format(i, node, ex))

            # get products
            products_node = html.findAll(name="a", attrs={"class": "product__link"})
            for node in products_node:
                try:
                    data = ET.fromstring(str(node))
                    name = ""
                    price = ""

                    url_product = "https://www.marksandspencer.com" + data.attrib["href"]
                    product_id = re.search('/p/([a-zA-Z0-9]+)?', url_product, re.IGNORECASE).group(1)
                    for subnode in data.findall("./div[@class='product__details']/"):
                        if subnode.attrib["class"] == "product__title":
                            name = subnode.text
                        if subnode.attrib["class"] == "product__price":
                            if len(subnode) == 0:
                                price = re.search('.([0-9.]+)', subnode.text, re.IGNORECASE).group(1)
                            else:
                                price = re.search('.([0-9.]+)', subnode[0].text, re.IGNORECASE).group(1)
                    products.append(add_in_dictionary(shop=Shop.MS,
                                                      obj_id=product_id,
                                                      reference=None,
                                                      name=name,
                                                      price=price,
                                                      in_stock=True,
                                                      taxo1=taxo1,
                                                      taxo2=taxo2,
                                                      taxo3=taxo3,
                                                      url=url_product))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR,
                              shop=Shop.MS, message="Error node page {} : {} ({})".format(i, node, ex))

            i += 1
            if i > nb_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.MS, message=ex)
    return None


def parse_ms():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.MS, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.MS, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.MS, df=df)
