import requests
from requests.exceptions import RequestException
from contextlib import closing
from enum import Enum
import os
import datetime
import pandas as pd
import time


class ErrorLevel(Enum):
    MAJOR = "MAJOR"
    MAJOR_get_category = "MAJOR_get_category"
    MAJOR_get_inventory = "MAJOR_get_inventory"
    MAJOR_save = "MAJOR_save"
    MEDIUM = "MEDIUM"
    MINOR = "MINOR"
    INFORMATION = "INFORMATION"


class Shop(Enum):
    ASOS = "ASOS"
    HM = "HM"
    MS = "MS"
    NEWLOOK = "NEWLOOK"
    PRIMARK = "PRIMARK"
    TKMAXX = "TKMAXX"
    ZARA = "ZARA"
    GAP = "GAP"


class Comparison(Enum):
    IN = "IN"
    START_WITH = "START_WITH"
    EQUAL = "EQUAL"


DIRECTORY_OUTPUT = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp"
DIRECTORY_OUTPUT_BEFORE_CLEAN = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp/before_clean"
DIRECTORY_ERROR = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp"
DIRECTORY_AGGREGATE_FILES = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp/aggregated_files"

USER_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None)


def simple_get(url: str, header: str = None):
    time.sleep(1)
    try:
        with closing(requests.get(url, stream=True, headers=header)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def log_error(level: ErrorLevel, shop: Shop, message: str):
    # if ErrorLevel != ErrorLevel.MINOR:
    print("{} - {} - {}".format(datetime.datetime.now(), level.name, shop.name))

    file = open(os.path.join(DIRECTORY_ERROR, "errors.txt"), "a")
    file.write("{} - {} - {}\n".format(datetime.datetime.now(), level.name, shop.name))
    file.close()

    file = open(os.path.join(DIRECTORY_ERROR, shop.name + "_errors.txt"), "a")
    file.write("{} - {}\n".format(datetime.datetime.now(), level.name))
    file.write("{}\n".format(message))
    file.close()

    if ErrorLevel != ErrorLevel.MAJOR:
        file = open(os.path.join(DIRECTORY_ERROR, "_MAJOR_errors.txt"), "a")
        file.write("{} - {} - {}\n".format(datetime.datetime.now(), level.name, shop.name))
        file.close()


def save_output_before(shop: Shop, df: pd.DataFrame, now):
    df.to_csv(
        os.path.join(DIRECTORY_OUTPUT_BEFORE_CLEAN,
                     "{}_{}-{}-{}_before_clean.csv".format(shop.name, now.year, now.month, now.day)),
        index=False)


def save_output_after(shop: Shop, df: pd.DataFrame, now):
    df.to_csv(os.path.join(DIRECTORY_OUTPUT, "{}_{}-{}-{}.csv".format(shop.name, now.year, now.month, now.day)),
              index=False)


def save_output(shop: Shop, df: pd.DataFrame):
    now = datetime.datetime.now()
    save_output_before(shop=shop, df=df, now=now)

    df = df.sort_values(by=['id', 'reference', 'name', "taxo1", "taxo2", "taxo3"])
    df = df.drop_duplicates(subset=['id', 'reference', 'name'], keep="first")

    save_output_after(shop=shop, df=df, now=now)


def add_in_dictionary(shop: Shop, obj_id: str, reference: str, name: str, price, in_stock: bool, taxo1: str, taxo2: str,
                      taxo3: str, taxo4: str = None, url: str = None) -> {}:
    return {"shop": shop.name,
            "id": obj_id,
            "reference": reference,
            "name": name,
            "price": price,
            "inStock": in_stock,
            "taxo1": taxo1,
            "taxo2": taxo2,
            "taxo3": taxo3,
            "taxo4": taxo4,
            "URL": url,
            "date": datetime.datetime.now()}


def is_condition_true(input_value: [], conditions: {}):
    for taxo_level, value in conditions.items():

        if value["operator"] == Comparison.EQUAL:
            for comp_value in value["value"]:
                if comp_value.lower() == input_value[taxo_level].lower():
                    return True

        elif value["operator"] == Comparison.IN:
            for comp_value in value["value"]:
                if comp_value.lower() in input_value[taxo_level].lower():
                    return True

        elif value["operator"] == Comparison.START_WITH:
            for comp_value in value["value"]:
                if input_value[taxo_level].lower().startswith(comp_value.lower()):
                    return True
        else:
            raise Exception("invalid comparison operator: {}".format(value["operator"]))
    return False


def split_and_sort(df: pd.DataFrame, true_first: bool, conditions: {}) -> [pd.DataFrame]:
    df["split_val"] = df.apply(lambda my_row:
                               is_condition_true(input_value=my_row, conditions=conditions),
                               axis=1)

    df_1 = df.loc[df['split_val'] == True].copy()
    if "taxo4" in df_1.columns:
        df_1 = df_1.sort_values(by=["taxo1", "taxo2", "taxo3", "taxo4"])
    else:
        df_1 = df_1.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_1 = df_1.drop(["split_val"], axis=1)

    df_2 = df.loc[df['split_val'] == False].copy()
    if "taxo4" in df_2.columns:
        df_2 = df_2.sort_values(by=["taxo1", "taxo2", "taxo3", "taxo4"])
    else:
        df_2 = df_2.sort_values(by=["taxo1", "taxo2", "taxo3"])
    df_2 = df_2.drop(["split_val"], axis=1)

    if true_first:
        return [df_1, df_2]
    else:
        return [df_2, df_1]
