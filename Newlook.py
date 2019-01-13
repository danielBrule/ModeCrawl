from Parser.Utils import *
import pandas as pd
import json

URL_NEWLOOK_CATEGORIES = "https://www.newlook.com/uk/sitemap/maps/sitemap_uk_category_en_1.xml"
URL_NEWLOOK_MENU_PAGE_MEN = "https://www.newlook.com/uk/json/meganav/tier-one/uk-mens"
URL_NEWLOOK_MENU_PAGE_WOMEN = "https://www.newlook.com/uk/json/meganav/tier-one/uk-womens"
URL_NEWLOOK_MENU_PAGE_KIDS = "https://www.newlook.com/uk/json/meganav/tier-one/uk-teens"


def my_find(node_value: str, dictionary: {}) -> []:
    output = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            output = output + my_find(node_value, value)
        if isinstance(value, list):
            for subkey in value:
                output = output + my_find(node_value, subkey)
        if key == node_value:
            output.append(value)
    return output


def get_categories_new(category_url: str) -> pd.DataFrame:
    data = simple_get(category_url)
    data = json.loads(data)
    data = my_find(node_value="link", dictionary=data)
    data = [x for x in data if "trackerCode" in x and "url" in x]
    df = pd.DataFrame(data)
    df = df[["trackerCode", "url"]]

    new = df["trackerCode"].str.split("|", n=6, expand=True)
    df["taxo1"] = new[1]
    df["taxo2"] = new[2]
    df["taxo3"] = new[3]
    df["taxo4"] = new[4]
    df["taxo5"] = new[5]
    df["taxo6"] = new[6]

    df = df.loc[df["taxo1"].isin(["womens", "mens", "teens"])]
    df = df.loc[
        df["taxo2"].isin(["accessories", "clothing", "footwear", "bagsaccessories", "backtoschool", "essentials",
                          "curves", "goingout", "maternity", "petite", "tall"])]
    df["taxo3"] = df.apply(lambda row: row["taxo4"] if pd.isnull(row["taxo3"]) or row["taxo3"] == "department" or
                                                       row["taxo3"] == "department" else row["taxo3"],
                           axis=1)

    return df


def get_categories() -> pd.DataFrame:
    df1 = get_categories_new(URL_NEWLOOK_MENU_PAGE_MEN)
    df2 = get_categories_new(URL_NEWLOOK_MENU_PAGE_WOMEN)
    df3 = get_categories_new(URL_NEWLOOK_MENU_PAGE_KIDS)
    return pd.concat([df1, df2, df3])


def get_inventory(taxo1, taxo2, taxo3, url: str):
    url = "https://www.newlook.com/uk/" + url
    print("Category: {}".format(url))
    try:
        products = []
        i = 0
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
            if i >= number_of_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.NEWLOOK, message=ex)
    return None

def sort_and_save(df: pd.DataFrame) -> pd.DataFrame:
    df["is_subcat"] = df.apply(lambda my_row:
                               True
                               if "brands" in my_row["taxo3"].lower() or
                                  "collections" in my_row["taxo3"].lower() or
                                  "department" in my_row["taxo3"].lower() or
                                  "viewall" in my_row["taxo3"].lower() or
                                  "image" in my_row["taxo3"].lower() or
                                  "style" in my_row["taxo3"].lower()
                               else False, axis=1)
    #######################
    df_url_is_subcat = df.loc[df['is_subcat'] == True].copy()
    df_url_is_subcat = df_url_is_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_subcat = df_url_is_subcat.drop(["is_subcat"], axis=1)

    #######################
    df_url_is_not_subcat = df.loc[df['is_subcat'] == False].copy()
    df_url_is_not_subcat = df_url_is_not_subcat.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_url_is_not_subcat = df_url_is_not_subcat.drop(["is_subcat"], axis=1)

    #######################
    df = pd.concat([df_url_is_not_subcat, df_url_is_subcat], sort=False)
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")
    return df



def parse_newlook():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.NEWLOOK, message=ex)
        return

    df_url = df_url.head(2)

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["url"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.NEWLOOK, message=ex)
        return

    df = pd.concat(df_list)
    try:
        now = datetime.datetime.now()
        save_output_before(shop=Shop.NEWLOOK, df=df, now=now)
        df = sort_and_save(df)
        save_output_after(shop=Shop.NEWLOOK, df=df, now=now)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_save, shop=Shop.NEWLOOK, message=ex)
        return

parse_newlook()