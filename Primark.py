from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import os
import datetime
import json
import time

URL_PRIMARK_HOME = "https://www.primark.com/en/products"




def get_categories() -> pd.DataFrame:
    raw_html = simple_get(URL_PRIMARK_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')
    output = []

    results = html.findAll(name="nav", attrs={"class": "products-menu blue-menu"})
    for result in results:
        # ignore role nodes
        if "role" in result.attrs:
            continue

        # convert result to xml
        root_node = ET.fromstring(str(result))
        for node in root_node[0]:

            # ignore node with class <> "active has-sub"
            if node.attrib["class"] != 'active has-sub':
                continue

            # get category
            category = node[0].attrib["data-category"]

            # for all sub category
            for category_node in node[1]:
                # get sub category name
                sub_category = category_node[0].attrib["data-breadcrumb"]

                # if sub category has sub sub category then read them
                if "class" in category_node.attrib and \
                        category_node.attrib["class"] == 'active has-sub':
                    # get info on the sub sub category
                    for sub_category_node in category_node[1]:
                        # read sub sub category
                        sub_sub_category = sub_category_node[0].attrib["data-breadcrumb"]
                        category_name = sub_category_node[0].attrib["data-category"]

                        output.append({"taxo1": category,
                                       "taxo2": sub_category,
                                       "taxo3": sub_sub_category,
                                       "category": category_name})

                else:
                    # get info on the sub category
                    category_name = category_node[0].attrib["data-category"]
                    output.append({"taxo1": category,
                                   "taxo2": sub_category,
                                   "taxo3": "",
                                   "category": category_name})

    # convert list of dictionary to df and remove duplicates
    output = pd.DataFrame(output)
    output = output.drop_duplicates()
    return output


def get_inventory(taxo1, taxo2, taxo3, category):
    print("Category: {}".format(category))
    time.sleep(1)

    products = []
    i = 1
    while True:
        data = simple_get("https://m.primark.com/admin/productsapi/search//{}/{}".format(category, i))
        i += 1
        time.sleep(1)
        if data is None:
            break;
        data = json.loads(data)

        if len(data["Products"]) == 0:
            break

        for node in data["Products"]:
            products.append({"shop": "Primark",
                             "id": node["BusinessId"],
                             "reference": node["Sku"],
                             "name": node["Title"],
                             "price": int(node["PriceInteger"]) * 100 + int(node["PriceDecimal"]),
                             "taxo1": taxo1,
                             "taxo2": taxo2,
                             "taxo3": taxo3})
    return (pd.DataFrame(products))


def parse_primark():
    # get url to analyse
    df_url = get_categories()
    df_url = df_url[df_url.taxo1.isin(["men", "women", "kids"])]
    #  get inventory

    df_list = [get_inventory(taxo1=row["taxo1"],
                             taxo2=row["taxo2"],
                             taxo3=row["taxo3"],
                             category=row["category"])
               for index, row in df_url.iterrows()]

    df = pd.concat(df_list)
    now = datetime.datetime.now()
    df.to_csv(os.path.join(DIRECTORY_TMP, "primark_{}-{}-{}.csv".format(now.year, now.month, now.day)))


parse_primark()
