from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import os
import datetime
import json
import time

URL_NEWLOOK_CATEGORIES = "https://www.newlook.com/uk/sitemap/maps/sitemap_uk_category_en_1.xml"

def get_categories() -> pd.DataFrame:
    data = simple_get(URL_NEWLOOK_CATEGORIES)
    data = json.loads(data)

    # todo
    # get URL
    # get taxo 1 for all
    #    (i.e. all string between www.newlook.com/uk/.../c/
    # split # on / and gather string 1 2 3
    # return DF(taxo1, taxo2, taxo3, URL)


def get_inventory(taxo1, taxo2, taxo3, URL):
    products = []
    i = 1
    while True:
        data = simple_get("{}/data-48.json?currency=GBP&language=en&page={}".format(URL, i))
        data = json.loads(data)
        # get number of page in data/numberOfPages

        # for node in data["data"]["results"]:
        #     products.append({"shop": "Newlook",
        #                      "id": # get product ID ,
        #                      "reference": # get product ID 2 ,
        #                      "name": # get product name,
        #                      "price": # get price),
        #                      "taxo1": taxo1,
        #                      "taxo2": taxo2,
        #                      "taxo3": taxo3})


        i += 1
        # if i > numberOfPages
            # break
    return (pd.DataFrame(products))


def parse_newlook():
    # get url to analyse
    df_url = get_categories()
    #  get inventory

    df_list = [get_inventory(taxo1=row["taxo1"],
                             taxo2=row["taxo2"],
                             taxo3=row["taxo3"],
                             category=row["category"])
               for index, row in df_url.iterrows()]

    df = pd.concat(df_list)
    now = datetime.datetime.now()
    df.to_csv(os.path.join(DIRECTORY_TMP, "Newlook_{}-{}-{}.csv".format(now.year, now.month, now.day)))
