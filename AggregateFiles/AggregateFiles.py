from Parser.Utils import *


class taxonomie_level1(Enum):
    MAN = "MAN"
    WOMAN = "WOMAN"
    KID = "KID"


def read_files(shop: Shop) -> pd.DataFrame:
    csv_files = [f for f in os.listdir(DIRECTORY_OUTPUT)
                 if os.path.isfile(os.path.join(DIRECTORY_OUTPUT, f)) and
                 f.endswith(".csv") and
                 shop.value in f and
                 "before_clean" not in f]
    df_list = [pd.read_csv(os.path.join(DIRECTORY_OUTPUT, f)) for f in csv_files]
    df = pd.concat(df_list, sort=False)
    return df


def get_clean_asos() -> pd.DataFrame:
    df = read_files(Shop.ASOS)
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "women": taxonomie_level1.WOMAN.value})
    return df


def get_clean_HM() -> pd.DataFrame:
    df = read_files(Shop.HM)
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "ladies": taxonomie_level1.WOMAN.value,
                                 "kids": taxonomie_level1.KID.value})
    return df


def get_clean_MS() -> pd.DataFrame:
    df = read_files(Shop.MS)
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "women": taxonomie_level1.WOMAN.value,
                                 "kids": taxonomie_level1.KID.value})
    df.URL = df.apply(lambda x: x.URL if pd.isnull(x.url) else x.url, axis=1)
    df = df.drop(['url'], axis=1)
    df.shop = Shop.MS.value
    return df


def get_clean_NEWLOOK() -> pd.DataFrame:
    df = read_files(Shop.NEWLOOK)
    df.taxo1 = df.taxo1.replace({"mens": taxonomie_level1.MAN.value,
                                 "womens": taxonomie_level1.WOMAN.value,
                                 "girls": taxonomie_level1.KID.value})
    df = df[df.taxo1 != "homeware"]
    return df


def get_clean_GAP() -> pd.DataFrame:
    df = read_files(Shop.GAP)
    df.taxo1 = df.taxo2
    df.taxo2 = df.taxo3
    df.taxo3 = None
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "women": taxonomie_level1.WOMAN.value,
                                 "girls": taxonomie_level1.KID.value,
                                 "boys": taxonomie_level1.KID.value})
    return df


def get_clean_PRIMARK() -> pd.DataFrame:
    df = read_files(Shop.PRIMARK)
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "women": taxonomie_level1.WOMAN.value,
                                 "kids": taxonomie_level1.KID.value})
    df.price = df.price / 100
    df = df[df.name.notnull()]
    return df


def get_clean_TKMAXX() -> pd.DataFrame:
    df = read_files(Shop.TKMAXX)
    df.taxo1 = df.taxo1.replace({"men": taxonomie_level1.MAN.value,
                                 "mens-contemporary-designers": taxonomie_level1.MAN.value,
                                 "mens-mod-box": taxonomie_level1.MAN.value,
                                 "mens-gold-label ": taxonomie_level1.MAN.value,
                                 "women": taxonomie_level1.WOMAN.value,
                                 "womens-contemporary-designers": taxonomie_level1.WOMAN.value,
                                 "womens-plus-size": taxonomie_level1.WOMAN.value,
                                 "womens-gold-label": taxonomie_level1.WOMAN.value,
                                 "womens-mod-box": taxonomie_level1.WOMAN.value,
                                 "kids": taxonomie_level1.KID.value})
    df = df[(df.taxo1 != "clearance") &
            (df.taxo1 != "christmas") &
            (df.taxo1 != "gifts") &
            (df.taxo1 != "toys") &
            (df.taxo1 != "home")]
    return df


def get_clean_ZARA() -> pd.DataFrame:
    df = read_files(Shop.ZARA)
    df.price = df.price / 100
    df = df[df.name.notnull()]
    return df


def drop_duplicate(shop: Shop, df: pd.DataFrame):
    print("{} - {}".format(shop.value, len(df)))
    df = df.drop_duplicates(subset=['id', 'date'], keep="last")
    print("{} - {}".format(shop.value, len(df)))


def clean_and_aggregate_files():
    print("{} - {}".format(datetime.datetime.now(), Shop.ASOS))
    df_ASOS = get_clean_asos()
    df_ASOS.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.ASOS.value + ".csv"))
    drop_duplicate(Shop.ASOS, df_ASOS)

    print("{} - {}".format(datetime.datetime.now(), Shop.HM))
    df_HM = get_clean_HM()
    df_HM.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.HM.value + ".csv"))
    drop_duplicate(Shop.HM, df_HM)

    print("{} - {}".format(datetime.datetime.now(), Shop.MS))
    df_MS = get_clean_MS()
    df_MS.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.MS.value + ".csv"))
    drop_duplicate(Shop.MS, df_MS)

    print("{} - {}".format(datetime.datetime.now(), Shop.NEWLOOK))
    df_NEWLOOK = get_clean_NEWLOOK()
    df_NEWLOOK.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.NEWLOOK.value + ".csv"))
    drop_duplicate(Shop.NEWLOOK, df_NEWLOOK)

    print("{} - {}".format(datetime.datetime.now(), Shop.GAP))
    df_GAP = get_clean_GAP()
    df_GAP.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.GAP.value + ".csv"))
    drop_duplicate(Shop.GAP, df_GAP)

    print("{} - {}".format(datetime.datetime.now(), Shop.PRIMARK))
    df_PRIMARK = get_clean_PRIMARK()
    df_PRIMARK.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.PRIMARK.value + ".csv"))
    drop_duplicate(Shop.PRIMARK, df_PRIMARK)

    print("{} - {}".format(datetime.datetime.now(), Shop.TKMAXX))
    df_TKMAXX = get_clean_TKMAXX()
    df_TKMAXX.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.TKMAXX.value + ".csv"))
    drop_duplicate(Shop.TKMAXX, df_TKMAXX)

    print("{} - {}".format(datetime.datetime.now(), Shop.ZARA))
    df_ZARA = get_clean_ZARA()
    df_ZARA.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price" + Shop.ZARA.value + ".csv"))
    drop_duplicate(Shop.ZARA, df_ZARA)

    df = pd.concat([df_ASOS, df_HM, df_MS, df_NEWLOOK, df_GAP, df_PRIMARK, df_TKMAXX, df_ZARA], sort=False)
    df.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price.csv"), index=False)


clean_and_aggregate_files()
