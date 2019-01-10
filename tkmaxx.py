from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
import re
from bs4 import BeautifulSoup

URL_TKMAXX_HOME_SITEMAP = "https://www.tkmaxx.com/uk/en/sitemap.xml"
URL_TKMAXX_HOME = "https://www.tkmaxx.com/uk/en/"


def get_categories() -> pd.DataFrame:
    output = []

    raw_html = simple_get(URL_TKMAXX_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.findAll(name="div", attrs={"class": "sub-navigation-section__inner"})

    for node in results:
        node = ET.fromstring(str(node))
        taxo1 = node[0].attrib["data-categoryparent"]
        taxo2 = node[0].attrib["data-category"]
        for subnode in node[1]:
            try:
                if "class" in subnode.attrib and \
                        " sub-navigation-section-column column-2 " == subnode.attrib["class"]:
                    for subsubnode in subnode[0]:
                        if len(subsubnode) > 0 and "href" in subsubnode[0].attrib and \
                                "data-category" in subsubnode.attrib:
                            taxo3 = subsubnode.attrib["data-category"]
                            url = subsubnode[0].attrib["href"]
                            output.append({"taxo1": taxo1,
                                           "taxo2": taxo2,
                                           "taxo3": taxo3,
                                           "URL": url})
                elif len(subnode) > 0 and "href" in subnode[0].attrib and "data-category" in subnode.attrib:
                    taxo3 = subnode.attrib["data-category"]
                    url = subnode[0].attrib["href"]
                    output.append({"taxo1": taxo1,
                                   "taxo2": taxo2,
                                   "taxo3": taxo3,
                                   "URL": url})
            except Exception as ex:
                print("{}".format(ex))
    output = pd.DataFrame(output)
    output = output.loc[output["taxo1"].isin(["Men", "Women", "Kids & Toys"])]
    return output


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    url = "https://www.tkmaxx.com/" + url
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
        print(len(df_url))
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


