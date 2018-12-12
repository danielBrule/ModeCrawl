from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json

URL_NEWLOOK_CATEGORIES = "https://www.newlook.com/uk/sitemap/maps/sitemap_uk_category_en_1.xml"


def get_categories() -> pd.DataFrame:
    # get url containing xml
    data = simple_get(URL_NEWLOOK_CATEGORIES)
    # get URL
    print(data)
    # convert result to xml
    root_node = ET.fromstring(data)
    print(root_node)

    raw_url_list = []
    for x in root_node:
        url_temp = x[0].text
        raw_url_list.append(url_temp)

    print('raw_url_list compiled')

    # Extract items in URL
    print('extract items in URL')
    splited_url_list = [x.split("/c/", 1)[0] for x in raw_url_list]
    print(splited_url_list[1])

    # Split piece of string obtained on "uk" and keep second half of split
    print('Split further on "uk"')
    splited_after_uk = [x.split("/uk/", 1)[1] for x in splited_url_list]
    print(splited_after_uk[1])

    # Split on "\" limiting to 4 splits
    print('Split further on " \ " to extract taxonomy')
    split_further = [x.split("/", 3) for x in splited_after_uk]
    print(split_further[0])

    # Place first 3 splits into a dict
    list_dict_taxo = []
    for i in range(len(split_further)):
        dict_temp = {'taxo1': split_further[i][0],
                     'taxo2': split_further[i][1] if len(split_further[i]) >= 2 else None,
                     'taxo3': split_further[i][2] if len(split_further[i]) >= 3 else None,
                     'URL': raw_url_list[i]}
        list_dict_taxo.append(dict_temp)
    print('list_dict_taxo  generated')

    df_dict_taxo = pd.DataFrame(list_dict_taxo)

    return df_dict_taxo


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print('start get_inventory function with URL {}'.format(url))
    try:
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
    save_output(shop=Shop.ASOS, df=df)


parse_newlook()
