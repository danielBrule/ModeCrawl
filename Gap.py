from Parser.Utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
import re

URL_GAP_HOME = "https://www.gap.co.uk/"
URL_GAP_HOME_CATEGORY = "https://www.gap.co.uk/sitemap_2-category.xml"
BASE_URL = "https://www.gap.co.uk/on/demandware.store/Sites-ShopUK-Site/en_GB/Product-LazyLoadBatchTiles?pids=%5B%"
BASE_URL_END = "5D&cgid=1110339&ulid=1110339"


# todo get sub categories
def get_categories() -> pd.DataFrame:
    sitemap_product_url = []
    sitemap_category_xml = simple_get(URL_GAP_HOME_CATEGORY)
    sitemap_category_root_node = ET.fromstring(sitemap_category_xml)
    for category in sitemap_category_root_node:
        sitemap_product_url.append(category[0].text)

    sitemap_product_url = [x for x in sitemap_product_url if "gap/men" in x or "gap/women" in x or "gap/boys" in x
                           or "gap/girls" in x]
    output = []
    for url in sitemap_product_url:
        taxonomy = url.replace('https://www.gap.co.uk/gap/', '')
        taxonomy = taxonomy.split("/")
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "taxo4": (taxonomy[3] if len(taxonomy) > 3 else None),
                       "URL": url})
    output = pd.DataFrame(output)
    return output


def parse_json(taxo1: str, taxo2: str, taxo3: str, taxo4: str, output: [], url: str) -> []:
    data = simple_get(url)
    data = json.loads(data)
    for node in data["productHits"]:
        try:
            price = None
            for price_node in node['prices']:
                try:
                    if len(price_node) != 0:
                        tmp_price = price_node['value'][1:]
                        if price is None or tmp_price < price:
                            price = tmp_price
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.GAP,
                              message="PARSE JSON FOR PRICE{}: {}".format(url, ex))
            output.append(add_in_dictionary(shop=Shop.GAP,
                                            obj_id=node['id'],
                                            reference=node['uuid'],
                                            name=node['name'],
                                            price=price,
                                            in_stock=True,
                                            taxo1=taxo1,
                                            taxo2=taxo2,
                                            taxo3=taxo3,
                                            taxo4=taxo4,
                                            url=None))
        except Exception as ex:
            log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="PARSE JSON {}: {}".format(url, ex))
    return output


class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')


@Singleton
class GapListProductsAlreadyParsedSingleton:
    product_list = []

    def get_product_list(self, new_products: []) -> []:
        print(len(self.product_list))
        output = set(new_products) - set(self.product_list)
        self.product_list = self.product_list + list(output)
        return output


def get_page_inventory(taxonomy: [str], last_level: str, url: str) -> pd.DataFrame:
    try:
        print('suburl: {}'.format(url))
        taxonomy = taxonomy.copy()
        taxonomy.append(last_level)
        products = []


        if 'parentCategory' in url:
            url = url[:url.rfind("/")+1]


        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        nb_item = re.findall('([0-9]+) item', str(html), re.IGNORECASE)[0]

        url = url + "/?sz={}&start=0&format=page-element".format(nb_item)
        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        product_node = html.findAll(name="div", attrs={"class": "sds_g-inner sds_grid-inner "})
        for node in product_node:
            try:
                products.append(node["data-loopproducthit"])
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="HTML parsing: {}".format(ex))

        products = GapListProductsAlreadyParsedSingleton.instance().get_product_list(products)
        if len(products) == 0:
            return None
        url = BASE_URL
        i = 0
        output = []
        for product in products:
            url = url + "22" + product + "%22%2C%"
            i += 1
            if i % 40 == 0:
                url = url[:-3] + BASE_URL_END
                try:
                    output = parse_json(taxo1=taxonomy[0] if len(taxonomy) >= 1 else None,
                                        taxo2=taxonomy[1] if len(taxonomy) >= 2 else None,
                                        taxo3=taxonomy[2] if len(taxonomy) >= 3 else None,
                                        taxo4=taxonomy[3] if len(taxonomy) >= 4 else None,
                                        output=output,
                                        url=url)
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="LOAD JSON: {}".format(ex))

        if i % 40 != 0:
            url = url[:-3] + BASE_URL_END
            try:
                output = parse_json(taxo1=taxonomy[0] if len(taxonomy) >= 1 else None,
                                    taxo2=taxonomy[1] if len(taxonomy) >= 2 else None,
                                    taxo3=taxonomy[2] if len(taxonomy) >= 3 else None,
                                    taxo4=taxonomy[3] if len(taxonomy) >= 4 else None,
                                    output=output,
                                    url=url)
            except Exception as ex:
                log_error(level=ErrorLevel.MINOR, shop=Shop.GAP, message="LOAD JSON: {}".format(ex))

        return pd.DataFrame(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.GAP, message=ex)


def get_inventory(taxo1: str, taxo2: str, taxo3: str, taxo4: str, url: str) -> pd.DataFrame:
    try:
        print("url {}: {}".format(Shop.GAP.value, url))

        output = []

        taxonomy = [taxo1, taxo2, taxo3, taxo4]
        taxonomy = [x for x in taxonomy if x is not None]

        raw_html = simple_get(url)
        html = BeautifulSoup(raw_html, 'html.parser')

        category_node = html.findAll(name="a", attrs={"class": "category-name"})
        for position in range (len(category_node) - 1, -1, -1):
            xml_node = ET.fromstring(str(category_node[position]))
            if "href" in xml_node.attrib:
                output.append(get_page_inventory(taxonomy=taxonomy,
                                                 last_level=xml_node.text.strip(),
                                                 url=URL_GAP_HOME + xml_node.attrib["href"]))


        return pd.concat(output)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.GAP, message=ex)
    return None


def sort_categories(df: pd.DataFrame) -> pd.DataFrame:
    conditions_sale = {"taxo1":
                           {"operator": Comparison.EQUAL,
                            "value": ["sale", "deals", "new-and-now"]
                            },
                       "taxo2":
                           {"operator": Comparison.START_WITH,
                            "value": ["last-", "up-to-","sale", "deals", "new-and-now"]
                            },
                       "taxo3":
                           {"operator": Comparison.START_WITH,
                            "value": ["last-", "up-to-"]
                            }
                       }

    conditions_new = {"taxo2":
                          {"operator": Comparison.IN,
                           "value": ["new-and-now", "special-sizes", "featured-shops", "gapbody",
                                     "the-schoolwear-shop"]
                           }
                      }

    output_1 = split_and_sort(df=df, true_first=False, conditions=conditions_sale)
    df_1 = output_1[0]

    output_2 = split_and_sort(df=df_1, true_first=False, conditions=conditions_new)
    df_1_1 = output_2[0]
    df_1_2 = output_2[1]

    df_2 = output_1[1]
    return pd.concat([df_1_1, df_1_2, df_2], sort=False)


def parse_gap():
    try:
        df_url = get_categories()

        # remove lines if next lines cover it (i.e. if you have a/b and a/b/c, a/b/d,a/b/e, then remove a/b)
        df_url = df_url.sort_values(by="URL")
        df_url["URL_next_line"] = df_url['URL'].shift(-1)
        df_url["is_in_next_row"] = df_url.apply(lambda row: str(row['URL']) in str(row["URL_next_line"]), axis=1)
        df_url = df_url.loc[df_url['is_in_next_row'] == False]
        df_url = df_url.drop(["URL_next_line", "is_in_next_row"], axis=1)

        # put sales categories at the end
        df_url = sort_categories(df=df_url)
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.GAP, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 taxo4=row["taxo4"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.GAP, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.GAP, df=df)
