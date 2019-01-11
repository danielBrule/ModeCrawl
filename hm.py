from Parser.Utils import *
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET
import json

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


def get_inventory(taxo1: str, url: str):
    print("{} - Category: {}".format(Shop.HM.name, url))
    try:
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        results = html.findAll(name="form", attrs={"class": "js-product-filter-form"})
        if len(results) > 1:
            log_error(level=ErrorLevel.INFORMATION, shop=Shop.HM, message="more than one node: {}".format(results))
        if len(results) == 0:
            log_error(level=ErrorLevel.INFORMATION, shop=Shop.HM, message="empty node")
            return None
        json_url = "https://www2.hm.com" + results[0].attrs["data-filtered-products-url"] + "?page-size=999"
        data = simple_get(json_url)
        data = json.loads(data)

        products = []
        for node in data["products"]:
            try:
                taxo = node["favouritesTracking"].split("|")[-1].split(":")
                taxo = [x.strip() for x in taxo]
                tmp_taxo2 = taxo[1] if len(taxo) >= 2 else None
                tmp_taxo3 = taxo[2] if len(taxo) >= 3 else None
                if (isinstance(tmp_taxo2, str) and tmp_taxo2 in ["BASICS_BASICS"]) or \
                        (isinstance(tmp_taxo3, str) and
                         tmp_taxo3 in [" BASICS_VIEW_ALL", "BEST BASICS_VIEW_ALL", "BESTBASICS"]):
                    continue
                products.append(add_in_dictionary(shop=Shop.HM,
                                                  obj_id=node["articleCode"],
                                                  reference=None,
                                                  name=node["title"],
                                                  price=node["price"][1:],
                                                  in_stock=True if node["outOfStockText"] == "" else False,
                                                  taxo1=taxo1,
                                                  taxo2=tmp_taxo2,
                                                  taxo3=tmp_taxo3,
                                                  url="https://www2.hm.com/" + node["swatches"][0]["articleLink"]))
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.HM, message=ex)
        return pd.DataFrame(products)

    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.HM, message=ex)
    return None


def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    df["is_subcat"] = df.apply(lambda my_row:
                               True
                               if "extended sizes_extended sizes" in my_row["taxo2"].lower() or
                                  "extendedsizes_extendedsizes" in my_row["taxo2"].lower() or
                                  "h&m+ plus sizes_h&m+ plus sizes" in my_row["taxo2"].lower() or
                                  "maternity wear_maternity wear" in my_row["taxo2"].lower() or
                                  "nightwear_nightwear" in my_row["taxo2"].lower()
                               else False, axis=1)

    df_url_is_subcat = df.loc[df['is_subcat'] == True].copy()
    df_url_is_subcat = df_url_is_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_subcat = df_url_is_subcat.drop(["is_subcat"], axis=1)

    df_url_is_not_subcat = df.loc[df['is_subcat'] == False].copy()
    df_url_is_not_subcat = df_url_is_not_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_not_subcat = df_url_is_not_subcat.drop(["is_subcat"], axis=1)

    df = pd.concat([df_url_is_not_subcat, df_url_is_subcat], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df


def parse_hm():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.HM, message=ex)
        return
    print(len(df_url))
    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.HM, message=ex)
        return

    df = pd.concat(df_list)

    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.HM, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.HM, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.HM, message=ex)
        return


