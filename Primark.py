from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET

URL_PRIMARK_HOME = "https://www.primark.com/en/products"

DIRECTORY_TMP = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp"


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
            category = node[0].attrib["data-category"]
            for category_node in node[1]:
                sub_category = category_node[0].attrib["data-breadcrumb"]
                if "class" in category_node.attrib and \
                        category_node.attrib["class"] == 'active has-sub':
                    for sub_category_node in category_node[1]:
                        sub_sub_category = sub_category_node[0].attrib["data-breadcrumb"]
                        href = sub_category_node[0].attrib["data-href"]
                        output.append({"taxo1": category,
                                       "taxo2": sub_category,
                                       "taxo3": sub_sub_category,
                                       "href": "https://www.primark.com/" + href})

                else:
                    href = category_node[0].attrib["data-href"]
                    output.append({"taxo1": category,
                                   "taxo2": sub_category,
                                   "taxo3": "",
                                   "href": "https://www.primark.com/" + href})

    output = pd.DataFrame(output)
    output = output.drop_duplicates()
    return output


output = get_categories()
print(output)
