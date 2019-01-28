from Parser.Utils import *
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

URL_MS_HOME = "https://www.marksandspencer.com/"


def get_categories() -> pd.DataFrame:
    raw_html = simple_get(URL_MS_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

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


def get_page_inventory(taxonomy: [str], last_level: str, url: str) -> pd.DataFrame:
    try:
        print('suburl: {}'.format(url))
        taxonomy = taxonomy.copy()
        taxonomy.append(last_level)

        i = 1
        products = []
        while True:
            url_prod = url + "?pageChoice={}".format(i)
            raw_html = simple_get(url_prod)
            html = BeautifulSoup(raw_html, 'html.parser')

            # get number of page
            nb_pages = html.findAll(name="span", attrs={"class": "pagination__page-x-of-y"})
            nb_pages = str(nb_pages[0].contents[1])
            nb_pages = int(re.search('[0-9]+ of ([0-9]+)', nb_pages, re.IGNORECASE).group(1))

            # get highlighted products
            spotlight_node = html.findAll(name="a", attrs={"class": "product"})
            for node in spotlight_node:
                try:
                    data = ET.fromstring(str(node))
                    name = ""
                    price = ""

                    url_product = URL_MS_HOME + data.attrib["href"]
                    product_id = re.search('/p/([a-zA-Z0-9]+)?', url_product, re.IGNORECASE).group(1)
                    for subnode in data.findall('./*/'):
                        if subnode.attrib["class"] == "product__title":
                            name = subnode.text.strip()
                        if subnode.attrib["class"] == 'product__price':
                            price = re.search('.([0-9.]+\.?[0-9]*)', subnode[0][0].tail, re.IGNORECASE).group(1)
                    products.append(add_in_dictionary(shop=Shop.MS,
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
                              shop=Shop.MS, message="Error spotlight page {} : {} ({})".format(i, node, ex), url=url)

            i += 1
            if i > nb_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.MS, message=str(ex), url=url)
    return None


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    try:
        print("url: {}".format(url))
        output = []

        taxonomy = [taxo1, taxo2, taxo3]
        taxonomy = [x for x in taxonomy if x is not None]
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')
        filters = html.findAll(name="li", attrs={"class": "accordion__item"})

        try:
            for product_filter in filters:
                data = ET.fromstring(str(product_filter))
                if data[1][0].text.strip() == 'Product Type':
                    for subnode in data[2][0]:
                        name = re.search('(.*).\(.*\)', subnode[1][0].text.strip(), re.IGNORECASE).group(1)
                        output.append(get_page_inventory(taxonomy=taxonomy,
                                                         last_level=name,
                                                         url=URL_MS_HOME + subnode[1][0].attrib["href"]))
        except Exception as ex:
            log_error(level=ErrorLevel.MINOR, shop=Shop.MS, message=str(ex), url=url)

        if len(output) == 0:
            try:
                for product_filter  in filters:
                    data = ET.fromstring(str(product_filter ))
                    if data[1][0].text.strip() == 'Categories' or \
                            data[1][0].text.strip() == 'Category':
                        for subnode in data[2][0]:
                            name = re.search('(.*).\(.*\)', subnode[1][0].text.strip(), re.IGNORECASE).group(1)
                            output.append(get_page_inventory(taxonomy=taxonomy,
                                                             last_level=name,
                                                             url=URL_MS_HOME + subnode[1][0].attrib["href"]))
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.MS, message=str(ex), url=url)

        if len(output) == 0:
            try:
                for product_filter  in filters:
                    data = ET.fromstring(str(product_filter ))
                    if data[1][0].text.strip() == 'Style':
                        for subnode in data[2][0]:
                            name = re.search('(.*).\(.*\)', subnode[1][0].text.strip(), re.IGNORECASE).group(1)
                            output.append(get_page_inventory(taxonomy=taxonomy,
                                                             last_level=name,
                                                             url=URL_MS_HOME + subnode[1][0].attrib["href"]))
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.MS, message=str(ex), url=url)

        if len(output) == 0:
            output.append(get_page_inventory(taxonomy=taxonomy,
                                             last_level=None,
                                             url=url))

        return pd.concat(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.MS, message=str(ex), url=url)
    return None


def parse_ms():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.MS, message=str(ex))
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.MS, message=str(ex))
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.MS, df=df)
