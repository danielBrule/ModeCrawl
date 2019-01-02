from Parser.Utils import *
from bs4 import BeautifulSoup
import re
import json
import pandas as pd

URL_ZARA_HOME = "https://www.zara.com/uk/"


def get_categories() -> []:
    raw_html = simple_get(URL_ZARA_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.findAll(name="li", attrs={"data-layout": "products-category-view"})
    output = []
    for result in results:
        try:
            output.append(result.find("a")["href"])
        except:
            try:
                output.append(result.find("a")["data-href"])
            except Exception as ex:
                log_error(level=ErrorLevel.MEDIUM, shop=Shop.ZARA, message="Invalid category".format(ex))
    return output


def get_inventory(url: str):
    print("url: {}".format(url))
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')

    pattern = re.compile(r"window.zara.dataLayer\s+=\s+(\{.*?\});window.zara.viewPayload = window.zara.dataLayer")
    scripts = html.find_all("script", text=pattern)
    try:
        products = []
        for script in scripts:
            data = pattern.search(script.text).group(1)
            data = json.loads(data)

            for node in data["productGroups"][0]["products"]:
                try:
                    if "price" in node:
                        products.append(add_in_dictionary(shop=Shop.ZARA,
                                                          obj_id=node["id"],
                                                          reference=node["detail"]["reference"],
                                                          name=node["name"],
                                                          price=node["price"],
                                                          in_stock=True,
                                                          taxo1=node["sectionName"],
                                                          taxo2=node["familyName"],
                                                          taxo3=node["subfamilyName"],
                                                          url=""))
                    else:
                        products.append(add_in_dictionary(shop=Shop.ZARA,
                                                          obj_id=node["id"],
                                                          reference=node["detail"]["reference"],
                                                          name=node["bundleProductSummaries"][0]["name"],
                                                          price=node["bundleProductSummaries"][0]["price"],
                                                          in_stock=True,
                                                          taxo1=node["sectionName"],
                                                          taxo2=node["familyName"],
                                                          taxo3=node["subfamilyName"],
                                                          url=""))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.ZARA, message=ex)
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ZARA, message=ex)
    return None


def parse_zara():
    try:
        list_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.ZARA, message=ex)
        return

    try:
        df_list = [get_inventory(x) for x in list_url]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.ZARA, message=ex)
        return
    df = pd.concat(df_list)
    save_output(shop=Shop.ZARA, df=df)
