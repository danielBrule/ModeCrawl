from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import re

URL_MS_HOME = "https://www.marksandspencer.com/sitemap.xml"


def get_categories() -> pd.DataFrame:
    sitemap_xml = simple_get(URL_MS_HOME)
    sitemap_root_node = ET.fromstring(sitemap_xml)

    sitemap_url = []
    for href in sitemap_root_node:
        sitemap_url.append(href[0].text)

    sitemap_url = [x for x in sitemap_url if "men" in x or "women" in x or "kids" in x]

    sitemap_product_url_url = []
    for taxonomy in sitemap_url:
        sitemap_product_xml = simple_get(taxonomy)
        sitemap_product_root_node = ET.fromstring(sitemap_product_xml)
        for href in sitemap_product_root_node:
            sitemap_product_url_url.append(href[0].text)
    sitemap_product_url_url = [x for x in sitemap_product_url_url if "categories" in x]

    category_url = []
    for taxonomy in sitemap_product_url_url:
        sitemap_product_xml = simple_get(taxonomy)
        sitemap_product_category_root_node = ET.fromstring(sitemap_product_xml)
        for href in sitemap_product_category_root_node:
            category_url.append(href[0].text)
    category_url = [x for x in category_url if "/l/" in x]

    output = []
    for url in category_url:
        taxonomy = url.replace('https://www.marksandspencer.com/l/', '')
        taxonomy = taxonomy.split("/")
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "URL": url})
    output = pd.DataFrame(output)
    return output


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
                    products.append({"shop": "ms",
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
