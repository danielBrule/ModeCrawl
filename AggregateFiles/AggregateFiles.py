from Parser.Utils import *


class taxo_lvl1(Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    KID = "KID"


class taxo_lvl2(Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"


class taxo_lvl3(Enum):
    MEN_SWEATSHIRT = "SWEATSHIRT"
    MEN_JACKET = "JACKET/COAT"
    MEN_SHIRT = "SHIRT"
    MEN_TSHIRT = "TSHIRT"
    MEN_JEANS = "JEANS"

    WOMEN_SWEATSHIRT = "SWEATSHIRT"
    WOMEN_JACKET = "JACKET/COAT"
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


def create_output_df(df_man: pd.DataFrame, df_woman: pd.DataFrame) -> pd.DataFrame:
    df = pd.concat([df_man, df_woman], sort=False)
    df = df.drop(["taxo2", "taxo3"], axis='columns')
    df = df.rename({"new_taxo3": "taxo3"}, axis='columns')

    df["taxo2"] = ""
    df.loc[df.taxo3 == taxo_lvl3.MEN_SWEATSHIRT.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.MEN_JACKET.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.MEN_SHIRT.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.MEN_TSHIRT.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.MEN_JEANS.value, "taxo2"] = taxo_lvl2.BOTTOM.value

    df.loc[df.taxo3 == taxo_lvl3.WOMEN_SWEATSHIRT.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.WOMEN_JACKET.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.WOMEN_SHIRT.value, "taxo2"] = taxo_lvl2.TOP.value
    df.loc[df.taxo3 == taxo_lvl3.WOMEN_DRESS.value, "taxo2"] = taxo_lvl2.BOTTOM.value
    df.loc[df.taxo3 == taxo_lvl3.WOMEN_SKIRTS.value, "taxo2"] = taxo_lvl2.BOTTOM.value
    df.loc[df.taxo3 == taxo_lvl3.WOMEN_JEANS.value, "taxo2"] = taxo_lvl2.BOTTOM.value

    return df


def do_taxonomy(df: pd.DataFrame, value: str, taxo: taxo_lvl3) -> pd.DataFrame:
    value = value.lower()
    df["new_taxo3"] = df.apply(lambda my_row:
                               taxo.value
                               if value in str(my_row["name"]).lower()
                               else my_row["new_taxo3"], axis=1)
    return df


def do_taxonomy_not_1_value(df: pd.DataFrame, value: str, not_value: str, taxo: taxo_lvl3) -> pd.DataFrame:
    value = value.lower()
    not_value = not_value.lower()
    df["new_taxo3"] = df.apply(lambda my_row:
                               taxo.value
                               if value in str(my_row["name"]).lower() and
                                  not_value not in str(my_row["name"]).lower()
                               else my_row["new_taxo3"], axis=1)
    return df


def do_taxonomy_not_2_values(df: pd.DataFrame, value: str, not_value1: str, not_value2: str,
                             taxo: taxo_lvl3) -> pd.DataFrame:
    value = value.lower()
    not_value1 = not_value2.lower()
    not_value2 = not_value2.lower()
    df["new_taxo3"] = df.apply(lambda my_row:
                               taxo.value
                               if value in str(my_row["name"]).lower() and
                                  not_value1 not in str(my_row["name"]).lower() and
                                  not_value2 not in str(my_row["name"]).lower()
                               else my_row["new_taxo3"], axis=1)
    return df


def taxonomise_by_regexp(df_man: pd.DataFrame, df_woman: pd.DataFrame, shop: Shop) -> pd.DataFrame:
    df_man = do_taxonomy(df=df_man, value=" t-shirt", taxo=taxo_lvl3.MEN_TSHIRT)
    df_man = do_taxonomy(df=df_man, value=" t shirt", taxo=taxo_lvl3.MEN_TSHIRT)
    df_man = do_taxonomy_not_2_values(df=df_man, value=" shirt", not_value1=" t ", not_value2="polo",
                                      taxo=taxo_lvl3.MEN_SHIRT)
    df_man = do_taxonomy(df=df_man, value="jacket", taxo=taxo_lvl3.MEN_JACKET)
    df_man = do_taxonomy_not_1_value(df=df_man, value="coat", not_value="waiscoat", taxo=taxo_lvl3.MEN_JACKET)
    df_man = do_taxonomy(df=df_man, value="sweatshirt", taxo=taxo_lvl3.MEN_SWEATSHIRT)
    df_man = do_taxonomy(df=df_man, value="sweater", taxo=taxo_lvl3.MEN_SWEATSHIRT)
    df_man = do_taxonomy(df=df_man, value="hoodie", taxo=taxo_lvl3.MEN_SWEATSHIRT)
    df_man = do_taxonomy(df=df_man, value="jeans", taxo=taxo_lvl3.MEN_JEANS)

    df_woman = do_taxonomy(df=df_woman, value="sweatshirt", taxo=taxo_lvl3.WOMEN_SWEATSHIRT)
    df_woman = do_taxonomy(df=df_woman, value="sweater", taxo=taxo_lvl3.WOMEN_SWEATSHIRT)
    df_woman = do_taxonomy(df=df_woman, value="hoodie", taxo=taxo_lvl3.WOMEN_SWEATSHIRT)
    df_woman = do_taxonomy(df=df_woman, value=" shirt", taxo=taxo_lvl3.WOMEN_SHIRT)
    df_woman = do_taxonomy(df=df_woman, value="blouse", taxo=taxo_lvl3.WOMEN_SHIRT)
    df_woman = do_taxonomy(df=df_woman, value=" t-shirt", taxo=taxo_lvl3.WOMEN_SHIRT)
    df_woman = do_taxonomy(df=df_woman, value=" t shirt", taxo=taxo_lvl3.WOMEN_SHIRT)
    df_woman = do_taxonomy(df=df_woman, value="jacket", taxo=taxo_lvl3.WOMEN_JACKET)
    df_woman = do_taxonomy_not_1_value(df=df_woman, value="coat", not_value="waiscoat", taxo=taxo_lvl3.WOMEN_JACKET)
    df_woman = do_taxonomy(df=df_woman, value="skirt", taxo=taxo_lvl3.WOMEN_SKIRTS)
    df_woman = do_taxonomy(df=df_woman, value="dress", taxo=taxo_lvl3.WOMEN_DRESS)
    df_woman = do_taxonomy(df=df_woman, value="jeans", taxo=taxo_lvl3.WOMEN_JEANS)

    return create_output_df(df_man, df_woman, shop)


def get_clean_ASOS(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value})

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    df_man.loc[df_man.taxo2 == "t-shirts-vests", "new_taxo3"] = taxo_lvl3.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "shirts", "new_taxo3"] = taxo_lvl3.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "jackets-coats", "new_taxo3"] = taxo_lvl3.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "hoodies-sweatshirts", "new_taxo3"] = taxo_lvl3.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "jeans", "new_taxo3"] = taxo_lvl3.MEN_JEANS.value

    df_woman.loc[(df_woman.taxo2 == "tops") &
                 (df_woman.taxo3 == "sweatshirts"), "new_taxo3"] = taxo_lvl3.WOMEN_SWEATSHIRT.value
    df_woman.loc[(df_woman.taxo2 == "tops") &
                 ((df_woman.taxo3 == "shirts") | (df_woman.taxo3 == "casual-shirts") |
                  (df_woman.taxo3 == "shirts-blouses") | (df_woman.taxo3 == "check-shirts") |
                  (df_woman.taxo3 == "denim-shirts")), "new_taxo3"] = taxo_lvl3.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "coats-jackets", "new_taxo3"] = taxo_lvl3.WOMEN_JACKET.value
    df_woman.loc[df_woman.taxo2 == "skirts", "new_taxo3"] = taxo_lvl3.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "dresses", "new_taxo3"] = taxo_lvl3.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "jeans", "new_taxo3"] = taxo_lvl3.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_HM(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "ladies": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    df_man.loc[(df_man.taxo2 == "t-shirts-and-vests") &
               (df_man.taxo3 != "polo"), "new_taxo3"] = taxo_lvl3.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "shirts", "new_taxo3"] = taxo_lvl3.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "jackets-and-coats", "new_taxo3"] = taxo_lvl3.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "hoodies-and-sweatshirts", "new_taxo3"] = taxo_lvl3.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "jeans", "new_taxo3"] = taxo_lvl3.MEN_JEANS.value

    df_woman.loc[df_woman.taxo2 == "hoodies-sweatshirts", "new_taxo3"] = taxo_lvl3.WOMEN_SWEATSHIRT.value
    df_woman.loc[df_woman.taxo2 == "shirts-and-blouses", "new_taxo3"] = taxo_lvl3.WOMEN_SHIRT.value
    df_woman.loc[df_woman.taxo2 == "jackets-and-coats", "new_taxo3"] = taxo_lvl3.WOMEN_JACKET.value
    df_woman.loc[df_woman.taxo2 == "skirts", "new_taxo3"] = taxo_lvl3.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "dresses", "new_taxo3"] = taxo_lvl3.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "jeans", "new_taxo3"] = taxo_lvl3.WOMEN_JEANS.value

    return create_output_df(df_man, df_woman, shop)


def get_clean_MS(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})
    df.URL = df.apply(lambda x: x.URL if pd.isnull(x.url) else x.url, axis=1)
    df = df.drop(['url'], axis=1)
    df.shop = Shop.MS.value

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    return taxonomise_by_regexp(df_man=df_man, df_woman=df_woman, shop=shop)


def get_clean_NEWLOOK(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"mens": taxo_lvl1.MAN.value,
                                 "womens": taxo_lvl1.WOMAN.value,
                                 "girls": taxo_lvl1.KID.value})
    df = df[df.taxo1 != "homeware"]

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    return taxonomise_by_regexp(df_man=df_man, df_woman=df_woman, shop=shop)


def get_clean_GAP(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    tmp1_df = df[df.taxo1 == "gap"].copy()
    tmp2_df = df[df.taxo1 != "gap"].copy()
    tmp1_df.taxo1 = tmp1_df.taxo2
    tmp1_df.taxo2 = tmp1_df.taxo3
    tmp1_df.taxo3 = None
    df = pd.concat([tmp1_df, tmp2_df], sort=False)

    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "girls": taxo_lvl1.KID.value,
                                 "boys": taxo_lvl1.KID.value})

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    return taxonomise_by_regexp(df_man=df_man, df_woman=df_woman, shop=shop)


def get_clean_PRIMARK(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.taxo1 = df.taxo1.replace({"men": taxo_lvl1.MAN.value,
                                 "women": taxo_lvl1.WOMAN.value,
                                 "kids": taxo_lvl1.KID.value})
    df.price = df.price / 100
    df = df[df.name.notnull()]

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    df_man.loc[df_man.taxo2 == "T-Shirts", "new_taxo3"] = taxo_lvl3.MEN_TSHIRT.value
    df_man.loc[df_man.taxo2 == "Shirts", "new_taxo3"] = taxo_lvl3.MEN_SHIRT.value
    df_man.loc[df_man.taxo2 == "Coats & Jackets", "new_taxo3"] = taxo_lvl3.MEN_JACKET.value
    df_man.loc[df_man.taxo2 == "Hoodies & Sweatshirts", "new_taxo3"] = taxo_lvl3.MEN_SWEATSHIRT.value
    df_man.loc[df_man.taxo2 == "Jeans", "new_taxo3"] = taxo_lvl3.MEN_JEANS.value

    df_woman["new_taxo3"] = df_woman.apply(lambda my_row:
                                           taxo_lvl3.WOMEN_SWEATSHIRT.value
                                           if "hoody" in str(my_row["name"]).lower() or
                                              "sweatshirt" in str(my_row["name"]).lower()
                                           else my_row["new_taxo3"], axis=1)
    df_woman["new_taxo3"] = df_woman.apply(lambda my_row:
                                           taxo_lvl3.WOMEN_SHIRT.value
                                           if my_row["taxo2"] == "Tops" and
                                              (" shirt" in str(my_row["name"]).lower() or
                                               " blouse" in str(my_row["name"]).lower())
                                           else my_row["new_taxo3"], axis=1)
    df_woman.loc[df_woman.taxo2 == "Coats & Jackets", "new_taxo3"] = taxo_lvl3.WOMEN_JACKET.value
    df_woman.loc[df_woman.taxo2 == "Skirts", "new_taxo3"] = taxo_lvl3.WOMEN_SKIRTS.value
    df_woman.loc[df_woman.taxo2 == "Dresses", "new_taxo3"] = taxo_lvl3.WOMEN_DRESS.value
    df_woman.loc[df_woman.taxo2 == "Jeans", "new_taxo3"] = taxo_lvl3.WOMEN_JEANS.value

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

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()

    return taxonomise_by_regexp(df_man=df_man, df_woman=df_woman, shop=shop)


def get_clean_ZARA(shop: Shop) -> pd.DataFrame:
    df = read_files(shop)
    df.price = df.price / 100
    df = df[df.name.notnull()]

    df["new_taxo3"] = ""
    df_man = df[df.taxo1 == taxo_lvl1.MAN.value].copy()
    df_woman = df[df.taxo1 == taxo_lvl1.WOMAN.value].copy()
    return taxonomise_by_regexp(df_man=df_man, df_woman=df_woman, shop=shop)


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
