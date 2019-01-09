from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup

URL_NEWLOOK_CATEGORIES = "https://www.newlook.com/uk/sitemap/maps/sitemap_uk_category_en_1.xml"


def get_categories() -> pd.DataFrame:
    # get url containing xml
    data = simple_get(URL_NEWLOOK_CATEGORIES)
    # get URL
    # convert result to xml
    root_node = ET.fromstring(data)

    raw_url_list = []
    for x in root_node:
        url_temp = x[0].text
        raw_url_list.append(url_temp)

    splited_url_list = [x.split("/c/", 1)[0] for x in raw_url_list]

    # Split piece of string obtained on "uk" and keep second half of split
    splited_after_uk = [x.split("/uk/", 1)[1] for x in splited_url_list]
    split_further = [x.split("/", 3) for x in splited_after_uk]

    # Place first 3 splits into a dict
    list_dict_taxo = []
    for i in range(len(split_further)):
        dict_temp = {'taxo1': split_further[i][0],
                     'taxo2': split_further[i][1] if len(split_further[i]) >= 2 else None,
                     'taxo3': split_further[i][2] if len(split_further[i]) >= 3 else None,
                     'URL': raw_url_list[i]}
        list_dict_taxo.append(dict_temp)

    df_dict_taxo = pd.DataFrame(list_dict_taxo)

    return df_dict_taxo


def get_inventory(taxo1, taxo2, taxo3, url: str):
    print("Category: {}".format(url))
    try:
        try:
            raw_html = simple_get(url)
            html = BeautifulSoup(raw_html, 'html.parser')
            results = html.findAll(name="ol",
                                   attrs={"typeof": "BreadcrumbList", "class": "breadcrumb__list list--unordered"})
            root_node = ET.fromstring(str(results[0]))
            taxo = []
            for node in root_node:
                if node[0][0].text.lower() == "home":
                    continue
                else:
                    taxo.append(node[0][0].text)
            taxo1 = taxo[0] if len(taxo) >= 1 else taxo1
            taxo2 = taxo[1] if len(taxo) >= 2 else taxo2
            taxo3 = taxo[2] if len(taxo) >= 3 else taxo3
        except Exception as ex:
            log_error(level=ErrorLevel.MEDIUM, shop=Shop.NEWLOOK, message="error while getting taxonomy :{}".format(ex))

        products = []
        i = 1
        while True:
            data = simple_get("{}/data-48.json?currency=GBP&language=en&page={}".format(url, i))
            data = json.loads(data)

            # get number of pages the item in the URL is present on
            number_of_pages = data['data']['pagination']['numberOfPages']
            # Iterate inside the ["data"]["results"] node
            for node in data["data"]["results"]:
                try:
                    products.append(add_in_dictionary(shop=Shop.NEWLOOK,
                                                      obj_id=node['code'],
                                                      reference=None,
                                                      name=node['name'],
                                                      price=node['price']['value'],
                                                      in_stock=False if node['stock']['stockLevelStatus'][
                                                                            'code'] == "outOfStock" else True,
                                                      taxo1=taxo1,
                                                      taxo2=taxo2,
                                                      taxo3=taxo3,
                                                      url="https://www.newlook.com/" + node['url']))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.NEWLOOK, message=ex)
            i += 1
            if i > number_of_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.NEWLOOK, message=ex)
    return None

get_inventory(None, None, None, "https://www.newlook.com/uk/womens/clothing/womens-activewear/sports-hoodies/c/uk-womens-clothing-sportswear-hoodies")

def parse_newlook():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.NEWLOOK, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.NEWLOOK, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.NEWLOOK, df=df)
