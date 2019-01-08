from Parser.Utils import *


def get_product_available_day_1(df: pd.DataFrame) -> list:
    min_date = min(df['date'])
    df = df[df.date == min_date].new_id.tolist()

    return set(df)


def get_day1_data(df: pd.DataFrame) -> pd.DataFrame:
    min_date = min(df['date'])
    df = df[df.date == min_date]

    on = ["shop", "taxo1", "taxo2", "taxo3"]

    df = df.drop_duplicates(subset=["new_id"])
    df = df[on]
    df = df.groupby(on)["shop"].count()
    df = pd.DataFrame(df)
    df = df.rename(columns={"shop": "Total_item_day_1"})
    df = df.reset_index()
    return df


def compute_new_old_item(df: pd.DataFrame, item_available_day1: list, date: datetime,
                         df_total_day1_item: pd.DataFrame) -> pd.DataFrame:
    df = df[df.date == date]

    on = ["date", "shop", "taxo1", "taxo2", "taxo3"]
    on2 = [ "shop", "taxo1", "taxo2", "taxo3"]

    df_old = df[df['new_id'].isin(item_available_day1)]
    df_old = df_old.drop_duplicates(subset=["new_id"])
    df_old = df_old[on]
    df_old = df_old.groupby(on)["shop"].count()
    df_old = pd.DataFrame(df_old)
    df_old = df_old.rename(columns={"shop": "item_present_day1"})
    df_old = df_old.reset_index()

    df_new = df[-df['new_id'].isin(item_available_day1)]
    df_new = df_new.drop_duplicates(subset=["new_id"])
    df_new = df_new[on]
    df_new = df_new.groupby(on)["shop"].count()
    df_new = pd.DataFrame(df_new)
    df_new = df_new.rename(columns={"shop": "item_not_present_day1"})
    df_new = df_new.reset_index()

    output = df_new.merge(right=df_old, how="outer", on=on)
    output = output.merge(right=df_total_day1_item, how="left", on=on2)
    return output


def main():
    # load data
    df = pd.read_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "Aggregate_price.csv"))

    # set date format
    df["date"] = df["date"].apply(lambda x: x.split(" ")[0])
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors="coerce")

    # remove product out of stock
    df = df[df.inStock == True]

    # create unique ID
    df["new_id"] = df["shop"] + "_" + df["id"].map(str) + "_"

    # get item available at day 1
    item_available_day1 = get_product_available_day_1(df)

    df_total_day1_item = get_day1_data(df=df)

    # compute new/old per day
    output = []
    date = min(df['date']) + datetime.timedelta(days=1)
    end_date = datetime.datetime.strptime(datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d')
    while date <= end_date:
        output.append(compute_new_old_item(df=df, item_available_day1=item_available_day1, date=date,
                                           df_total_day1_item=df_total_day1_item))
        date = date + datetime.timedelta(days=1)

    output_df = pd.concat(output, sort=False)
    output_df.to_csv(os.path.join(DIRECTORY_AGGREGATE_FILES, "count_old_new_item.csv"), index=False)


main()
