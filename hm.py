from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import os
import datetime
import json
import time

URL_HM_HOME = "https://www2.hm.com/en_gb.pages.0.xml"


def get_categories() -> []:
    raw_xml = simple_get(URL_HM_HOME)
    root_node = ET.fromstring(raw_xml)

    href_list = []
    for href in root_node:
        href_list.append(href[0].text)

    href_list = [x for x in href_list
                 if "/men/shop-by-product/" in x or
                 "/ladies/shop-by-product/" in x or
                 "/kids/shop-by-product/" in x]
    href_list = [x for x in href_list if x.endswith(".html")]
    href_list = [x for x in href_list if "view-all" not in x]

    output = []
    for i in range(0, len(href_list[:-1])):
        element_1 = href_list[i][:-5]
        element_2 = href_list[i + 1]
        if not element_2.startswith(element_1):
            element_1 = element_1.replace('https://www2.hm.com/en_gb/', '')
            element_1 = element_1.split("/")
            output.append({"taxo1": element_1[0],
                           "taxo2": element_1[2],
                           "taxo3": (element_1[3] if len(element_1) > 3 else None),
                           "URL": href_list[i]})

    output = pd.DataFrame(output)
    return output


def get_inventory(taxo1, taxo2, taxo3, url):
    print("Category: {}".format(url))
    try:
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        results = html.findAll(name="form", attrs={"class": "js-product-filter-form"})
        if len(results) > 1:
            print("error : {}".format(results))
        if len(results) == 0:
            print("Empty node")
            return None
        json_url = "https://www2.hm.com" + results[0].attrs["data-filtered-products-url"]
        data = simple_get(json_url)
        data = json.loads(data)

        products = []
        for node in data["products"]:
            products.append({"shop": "HM",
                             "id": node["articleCode"],
                             "reference": None,
                             "name": node["title"],
                             "price": node["price"][1:],
                             "taxo1": taxo1,
                             "taxo2": taxo2,
                             "taxo3": taxo3})
        return (pd.DataFrame(products))
    except Exception as ex:
        print("Excetion on {}: {}".format(url, ex))
    return None

def parse_primark():
    # get url to analyse
    df_url = get_categories()
    df_list = [get_inventory(taxo1=row["taxo1"],
                             taxo2=row["taxo2"],
                             taxo3=row["taxo3"],
                             url=row["URL"])
               for index, row in df_url.iterrows()]
    df = pd.concat(df_list)
    now = datetime.datetime.now()
    df.to_csv(os.path.join(DIRECTORY_TMP, "hm_{}-{}-{}.csv".format(now.year, now.month, now.day)))


parse_primark()
