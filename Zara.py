import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import os
import time
from flask import Flask
app = Flask(__name__)

URL_ZARA_HOME = "https://www.zara.com/uk/"

DIRECTORY_TMP = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp"
FILE_ZARA_HOME = "zara_home.html"


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def simple_get(url):
    try:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def get_categories() -> []:
    raw_html = simple_get(URL_ZARA_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.findAll(name="li", attrs={"data-layout": "products-category-view"})
    output = []
    for result in results:
        try:
            output.append(result.find("a")["href"])
            # print(result)
        except:
            try:
                output.append(result.find("a")["data-href"])
            except:
                print(result)
    return output


def get_inventory(url: str):
    time.sleep(1)
    print(url)
    raw_html = simple_get(url)
    html = BeautifulSoup(raw_html, 'html.parser')

    pattern = re.compile(r"window.zara.dataLayer\s+=\s+(\{.*?\});window.zara.viewPayload = window.zara.dataLayer")
    scripts = html.find_all("script", text=pattern)
    try:
        for script in scripts:
            data = pattern.search(script.text).group(1)
            data = json.loads(data)

            products = []
            i = 0
            for node in data["productGroups"][0]["products"]:
                try:
                    if "price" in node:
                        products.append({"shop": "Zara",
                                         "id": node["id"],
                                         "reference": node["detail"]["reference"],
                                         "name": node["name"],
                                         "price": node["price"],
                                         "taxo1": node["sectionName"],
                                         "taxo2": node["familyName"],
                                         "taxo3": node["subfamilyName"]})
                    else:
                        products.append({"shop": "Zara",
                                         "id": node["id"],
                                         "reference": node["detail"]["reference"],
                                         "name": node["bundleProductSummaries"][0]["name"],
                                         "price": node["bundleProductSummaries"][0]["price"],
                                         "taxo1": node["sectionName"],
                                         "taxo2": node["familyName"],
                                         "taxo3": node["subfamilyName"]})

                except Exception as err:
                    i += 1
                    print("{}/{} : {}".format(i, len(data["productGroups"][0]["products"]),err))
            return(pd.DataFrame(products))
    except Exception:
        print("URL EXCEPTION: {}".format(url))
        return None

    results = html.findAll(name="")
    print(len(results))

def parse_zara():
    list_url = get_categories()

    df_list = [get_inventory(x) for x in list_url]
    df = pd.concat(df_list)
    df.to_csv(os.path.join(DIRECTORY_TMP, "zara.csv"))


@app.route("/")
def parse():
    parse_zara()
    return "Done!"