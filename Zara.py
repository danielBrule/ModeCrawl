from Parser.Utils import *
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import xml.etree.ElementTree as ET

URL_ZARA_HOME = "https://www.zara.com/uk/"


def parse_ul_node(main_node: ET, taxo: []) -> pd.DataFrame:
    output = []
    output_df = []
    for node in main_node:
        try:
            if node.tag != "li":
                continue
            taxo_tmp = taxo.copy()
            taxo_tmp.append(node.attrib["data-name"])

            if "href" in node[0].attrib:
                URL = "href"
            else:
                URL = "data-href"

            output.append({"taxo1": taxo_tmp[0],
                           "taxo2": taxo_tmp[1] if len(taxo_tmp) >= 2 else None,
                           "taxo3": taxo_tmp[2] if len(taxo_tmp) >= 3 else None,
                           "taxo4": taxo_tmp[3] if len(taxo_tmp) >= 4 else None,
                           "URL": node[0].attrib[URL]})
            if len(node) > 1:
                for subnode in node[1].iter():
                    output_df.append(parse_ul_node(main_node=subnode, taxo=taxo_tmp.copy()))
        except Exception as ex:
            print("{}".format(ex))

    output_df.append(pd.DataFrame(output))
    output_df = pd.concat(output_df)
    return output_df


def get_categories() -> []:
    raw_html = simple_get(URL_ZARA_HOME)
    html = BeautifulSoup(raw_html, 'html.parser')

    results = html.findAll(name="nav", attrs={"id": "menu", "class": "menu"})
    root_node = ET.fromstring(str(results[0]))

    output = parse_ul_node(main_node=root_node[1].iter(), taxo=[])

    #######################

    output = output.loc[output["taxo1"].isin(["WOMAN", "MAN", "KIDS"])]
    output["taxo2"] = output["taxo2"].apply(str)

    conditions = {"taxo2":
                      {"operator": Comparison.IN,
                       "value":
                           ["ACCESSORIES", "BLAZERS", "COATS", "DRESSES", "JACKETS", "JEANS", "KNITWEAR", "POLOS",
                            "SHIRTS", "SHIRTS | BLOUSES", "SHOES ", "SKIRTS", "SHORTS", "SUITS", "SWEATSHIRTS",
                            "TROUSERS", "T-SHIRTS"]
                       }
                  }
    output = split_and_sort(df=output, true_first=True, conditions=conditions)

    df = pd.concat([output[0], output[1]], sort=False)
    df = df.drop_duplicates(subset=['URL'], keep="first")

    return df


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("url: {}".format(url))
    raw_html = simple_get(url, USER_AGENT)
    html = BeautifulSoup(raw_html, 'html.parser')

    pattern = re.compile(r"window.zara.dataLayer\s+=\s+(\{.*?\});window.zara.viewPayload = window.zara.dataLayer")
    scripts = html.find_all("script", text=pattern)
    try:
        products = []
        print("scripts {}".format(len(scripts)))
        for script in scripts:
            data = pattern.search(script.text).group(1)
            data = json.loads(data)
            print(len(data["productGroups"][0]["products"]))
            for node in data["productGroups"][0]["products"]:
                try:
                    if "price" in node:
                        products.append(add_in_dictionary(shop=Shop.ZARA,
                                                          obj_id=node["id"],
                                                          reference=node["detail"]["reference"],
                                                          name=node["name"],
                                                          price=node["price"],
                                                          in_stock=True,
                                                          taxo1=taxo1,
                                                          taxo2=taxo2,
                                                          taxo3=taxo3,
                                                          url=""))
                    else:
                        products.append(add_in_dictionary(shop=Shop.ZARA,
                                                          obj_id=node["id"],
                                                          reference=node["detail"]["reference"],
                                                          name=node["bundleProductSummaries"][0]["name"],
                                                          price=node["bundleProductSummaries"][0]["price"],
                                                          in_stock=True,
                                                          taxo1=taxo1,
                                                          taxo2=taxo2,
                                                          taxo3=taxo3,
                                                          url=""))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.ZARA, message=ex)
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.ZARA, message=ex)
    return None


def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    conditions = {"taxo2":
                      {"operator": Comparison.IN,
                       "value":
                           ["FROM ", "Shoes | Bags", "NEW IN", "Collection", "Basics", "DRESS TIME", "JOIN LIFE",
                            "MUM", "MUST HAVE", "None"]
                       }
                  }

    output = split_and_sort(df=df, true_first=False, conditions=conditions)

    df = pd.concat([output[0], output[1]], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df


def parse_zara():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.ZARA, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]

    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.ZARA, message=ex)
        return
    df = pd.concat(df_list)

    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.ZARA, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.ZARA, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.ZARA, message=ex)
        return

