from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup

URL_TKMAXX_HOME_SITEMAP = "https://www.tkmaxx.com/uk/en/sitemap.xml"
URL_TKMAXX_HOME = "https://www.tkmaxx.com/uk/en/"


def get_categories() -> pd.DataFrame:
    print("{} get home sitemap".format(Shop.TKMAXX.value))
    sitemap_xml = simple_get(URL_TKMAXX_HOME_SITEMAP, USER_AGENT)
    sitemap_root_node = ET.fromstring(sitemap_xml)

    sitemap_url = []
    for href in sitemap_root_node:
        sitemap_url.append(href[0].text)

    sitemap_url = [x for x in sitemap_url if "Category-en-GBP" in x]

    print("{} get Category-en-GBP".format(Shop.TKMAXX.value))
    sitemap_product_xml = simple_get(sitemap_url[0], USER_AGENT)
    sitemap_product_root_node = ET.fromstring(sitemap_product_xml)

    print("{} parse Categories".format(Shop.TKMAXX.value))
    category_url = []
    for href in sitemap_product_root_node:
        category_url.append(href[0].text)

    output = []
    for url in category_url:
        taxonomy = url.replace('https://www.tkmaxx.com/uk/en/', '')
        taxonomy = taxonomy.split("/")
        taxonomy = taxonomy[:-2]
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "URL": url})
    output = pd.DataFrame(output)
    output["is_subcat"] = output.apply(lambda my_row:
                                       True
                                       if "men" in my_row["taxo1"].lower() or
                                          "women" in my_row["taxo1"].lower() or
                                          "kids" in my_row["taxo1"].lower()
                                       else False,
                                       axis=1)
    output = output.loc[output['is_subcat'] == True].copy()
    output = output.drop(["is_subcat"], axis=1)

    return output



def get_page_inventory(taxonomy: [str], last_level: str, url: str) -> pd.DataFrame:
    try:
        print(last_level)
        taxonomy = taxonomy.copy()
        taxonomy.append(last_level)
        products = []
        i = 0
        while True:
            raw_html = simple_get(url, USER_AGENT)
            html = BeautifulSoup(raw_html, 'html.parser')

            if "The page you were looking for does not exist" in html:
                return None

            last_level = last_level.replace(" ", "%20")
            data = simple_get(
                url + "/autoLoad?q=&sort=publishedDate-desc&facets=stockLevelStatus%3AinStock%3Astyle%3A{}&fetchAll=true&page={}".format(
                    last_level, i), USER_AGENT)

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
                                                      taxo1=taxonomy[0] if len(taxonomy) >= 1 else None,
                                                      taxo2=taxonomy[1] if len(taxonomy) >= 2 else None,
                                                      taxo3=taxonomy[2] if len(taxonomy) >= 3 else None,
                                                      taxo4=taxonomy[3] if len(taxonomy) >= 4 else None,
                                                      url="https://www.tkmaxx.com/uk/" + node['url']))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.TKMAXX, message=ex)
            i += 1
            if i >= number_of_pages:
                break
        df = pd.DataFrame(products)
        print("{} - {}".format(last_level, len(df)))
        return df
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.TKMAXX, message=ex)
    return None


def get_inventory(taxo1: str, taxo2: str, taxo3: str, taxo4: str, url: str) -> pd.DataFrame:
    try:
        url = "https://www.tkmaxx.com/" + url
        print("url: {}".format(url))

        output = []

        taxonomy = [taxo1, taxo2, taxo3, taxo4]
        taxonomy = [x for x in taxonomy if x is not None]

        style_data = simple_get(url + "/autoLoad?q=&page=0", USER_AGENT)

        data = json.loads(style_data)

        for node in data['facets']:
            if node["code"] == 'style':
                for style_node in node["values"]:
                    output.append(get_page_inventory(taxonomy=taxonomy,
                                                     last_level=style_node["code"],
                                                     url=url))

        return pd.concat(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.TKMAXX, message=ex)
    return None




def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    conditions_1 = {"taxo3":
                        {"operator": Comparison.IS_NUMBER,
                         "value": []
                         }
                    }
    conditions_2 = {"taxo2":
                        {"operator": Comparison.EQUAL,
                         "value": ["c", "biggest-savings", "clothing", "big-brand-delivery",
                                   "last-chance"]
                         },
                    "taxo3":
                        {"operator": Comparison.EQUAL,
                         "value": ["c", "clothing", "new-in-boys"]
                         }
                    }

    output = split_and_sort(df=df, true_first=False, conditions=conditions_1)
    output2 = split_and_sort(df=output[0], true_first=False, conditions=conditions_2)

    df = pd.concat([output2[0], output2[1], output[1]], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df


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
    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.TKMAXX, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.TKMAXX, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.TKMAXX, message=ex)
        return
