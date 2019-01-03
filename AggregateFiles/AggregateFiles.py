from Parser.Utils import *
import numpy as np


class taxo_lvl1(Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    KID = "KID"


class taxo_lvl2(Enum):
    MEN_SWEATSHIRT = "SWEATSHIRT"
    MEN_SHIRT = "SHIRT"
    MEN_TSHIRT = "TSHIRT"
    MEN_JACKET = "JACKET"
    MEN_JEANS = "JEANS"

    WOMEN_COAT = "COAT"
    WOMEN_SWEATSHIRT = "SWEATSHIRT"
    WOMEN_SHIRT = "SHIRT"
    WOMEN_DRESS = "DRESS"
    WOMEN_SKIRTS = "SKIRTS"
    WOMEN_JEANS = "JEANS"


def read_files(shop: Shop) -> pd.DataFrame:
    csv_files = [f for f in os.listdir(DIRECTORY_OUTPUT)
                 if os.path.isfile(os.path.join(DIRECTORY_OUTPUT, f)) and
                 f.endswith(".csv") and
                 shop.value in f and
                 "before_clean" not in f]
    df_list = [pd.read_csv(os.path.join(DIRECTORY_OUTPUT, f)) for f in csv_files]
    df = pd.concat(df_list, sort=False)
    return df


def create_output_df(df_man: pd.DataFrame, df_woman: pd.DataFrame, shop: Shop) -> pd.DataFrame:
    df = pd.concat([df_man, df_woman], sort=False)
    df = df.drop(["taxo2", "taxo3"], axis='columns')
    df = df.rename({"new_taxo2": "taxo2"}, axis='columns')
    tmp = df[df.taxo2 != ""]
    tmp.to_csv("todel_" + shop.value + ".csv")
    return df


def get_clean_ASOS(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value})

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "t-shirts-vests", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "shirts", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "jackets-coats", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[(df_man.taxo2 == "hoodies-sweatshirts") &
               (df_man.taxo3 == "sweatshirts"), "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "jeans", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[(df_woman.taxo2 == "tops") &
                 (df_woman.taxo3 == "sweatshirts"), "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[(df_woman.taxo2 == "tops") &
                 ((df_woman.taxo3 == "shirts") | (df_woman.taxo3 == "casual-shirts") |
                  (df_woman.taxo3 == "shirts-blouses") | (df_woman.taxo3 == "check-shirts") |
                  (df_woman.taxo3 == "denim-shirts")), "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "coats-jackets", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "skirts", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "dresses", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "jeans", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_HM(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "ladies": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_MS(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})
    df.URL = df.apply(lambda x: x.URL if pd.isnull(x.url) else x.url, axis=1)
    df = df.drop(['url'], axis=1)
    df.shop = Shop.MS.value

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_NEWLOOK(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"mens": taxo_lvl1.MAN.value,
                                 "womens": taxo_lvl1.WOMAN.value,
                                 "girls": taxo_lvl1.KID.value})
    df = df[df.taxo1 != "homeware"]

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_GAP(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    tmp1_df = df[df.taxo1 == "gap"]
    tmp2_df = df[df.taxo1 != "gap"]
    tmp1_df.taxo1 = tmp1_df.taxo2
    tmp1_df.taxo2 = tmp1_df.taxo3
    tmp1_df.taxo3 = None
    df = pd.concat([tmp1_df, tmp2_df], sort=False)

    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "girls": taxo_lvl1.KID.value,
                                 "boys": taxo_lvl1.KID.value})

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_PRIMARK(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})
    df.price = df.price / 100
    df = df[df.name.notnull()]

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_TKMAXX(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "mens-contemporary-designers": taxo_lvl1.MAN.value,
                                 "mens-mod-box": taxo_lvl1.MAN.value,
                                 "mens-gold-label": taxo_lvl1.MAN.value,
                                 "mens-early-access": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "womens-contemporary-designers": taxo_lvl1.WOMAN.value,
                                 "womens-plus-size": taxo_lvl1.WOMAN.value,
                                 "womens-gold-label": taxo_lvl1.WOMAN.value,
                                 "womens-mod-box": taxo_lvl1.WOMAN.value,
                                 "womens-early-access": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})
    df = df[(df.taxo1 != "clearance") &
            (df.taxo1 != "christmas") &
            (df.taxo1 != "gifts") &
            (df.taxo1 != "toys") &
            (df.taxo1 != "home")]

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_ZARA(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.price = df.price / 100
    df = df[df.name.notnull()]

    df["new_taxo2"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value]
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value]

    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_COAT.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "TODO", "new_taxo2"] = taxo_lvl2.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def drop_duplicate(shop: Shop, df: pd.DataFrame):
    len_before = len(df)
    df = df.drop_duplicates(subset=['id', 'date'], keep="last")
    if len_before != len(df):
        print("DUPLICATE DATE IN {}".format(shop.value))


def clean_and_aggregate_files():
    print("{} - {}".format(datetime.datetime.now(), Shop.ASOS))
    df_ASOS = get_clean_ASOS(shop=Shop.ASOS)
    df_ASOS.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.ASOS.value + ".csv"))
    drop_duplicate(Shop.ASOS, df_ASOS)

    print("{} - {}".format(datetime.datetime.now(), Shop.HM))
    df_HM = get_clean_HM(shop=Shop.HM)
    df_HM.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.HM.value + ".csv"))
    drop_duplicate(Shop.HM, df_HM)

    print("{} - {}".format(datetime.datetime.now(), Shop.MS))
    df_MS = get_clean_MS(shop=Shop.MS)
    df_MS.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.MS.value + ".csv"))
    drop_duplicate(Shop.MS, df_MS)

    print("{} - {}".format(datetime.datetime.now(), Shop.NEWLOOK))
    df_NEWLOOK = get_clean_NEWLOOK(shop=Shop.NEWLOOK)
    df_NEWLOOK.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.NEWLOOK.value + ".csv"))
    drop_duplicate(Shop.NEWLOOK, df_NEWLOOK)

    print("{} - {}".format(datetime.datetime.now(), Shop.GAP))
    df_GAP = get_clean_GAP(shop=Shop.GAP)
    df_GAP.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.GAP.value + ".csv"))
    drop_duplicate(Shop.GAP, df_GAP)

    print("{} - {}".format(datetime.datetime.now(), Shop.PRIMARK))
    df_PRIMARK = get_clean_PRIMARK(shop=Shop.PRIMARK)
    df_PRIMARK.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.PRIMARK.value + ".csv"))
    drop_duplicate(Shop.PRIMARK, df_PRIMARK)

    print("{} - {}".format(datetime.datetime.now(), Shop.TKMAXX))
    df_TKMAXX = get_clean_TKMAXX(shop=Shop.TKMAXX)
    df_TKMAXX.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.TKMAXX.value + ".csv"))
    drop_duplicate(Shop.TKMAXX, df_TKMAXX)

    print("{} - {}".format(datetime.datetime.now(), Shop.ZARA))
    df_ZARA = get_clean_ZARA(shop=Shop.ZARA)
    df_ZARA.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.ZARA.value + ".csv"))
    drop_duplicate(Shop.ZARA, df_ZARA)

    df = pd.concat([df_ASOS, df_HM, df_MS, df_NEWLOOK, df_GAP, df_PRIMARK, df_TKMAXX, df_ZARA], sort=False)
    df.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price.csv"), index=False)


clean_and_aggregate_files()
