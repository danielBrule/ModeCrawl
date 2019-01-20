from Parser.Utils import *
import pandas as pd
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

URL_MS_HOME = "https://www.marksandspencer.com/sitemap.xml"

# TODO
# get all node
# <a ... data-cmspot-id="SC_Level_1_11563899" class="nav-primary__menu-link">
# get all nodes
# < div data - mns - sub - navigation - menu = "SC_Level_1_11563899" id = "SC_Level_1_11563899">
# parse them


def get_categories() -> pd.DataFrame:
    sitemap_xml = simple_get(URL_MS_HOME)
    sitemap_root_node = ET.fromstring(sitemap_xml)

    sitemap_url = []
    for href in sitemap_root_node:
        sitemap_url.append(href[0].text)

    sitemap_url = [x for x in sitemap_url if "men" in x or "women" in x or "kids" in x]

    sitemap_product_url_url = []
    for taxonomy in sitemap_url:
        sitemap_product_xml = simple_get(taxonomy)
        sitemap_product_root_node = ET.fromstring(sitemap_product_xml)
        for href in sitemap_product_root_node:
            sitemap_product_url_url.append(href[0].text)
    sitemap_product_url_url = [x for x in sitemap_product_url_url if "1facet" in x]

    category_url = []
    for taxonomy in sitemap_product_url_url:
        sitemap_product_xml = simple_get(taxonomy)
        sitemap_product_category_root_node = ET.fromstring(sitemap_product_xml)
        for href in sitemap_product_category_root_node:
            category_url.append(href[0].text)
    category_url = [x for x in category_url if "/l/" in x]

    output = []
    for url in category_url:
        taxonomy = url.replace('https://www.marksandspencer.com/l/', '')
        taxonomy = taxonomy.split("/")
        output.append({"taxo1": taxonomy[0],
                       "taxo2": (taxonomy[1] if len(taxonomy) > 1 else None),
                       "taxo3": (taxonomy[2] if len(taxonomy) > 2 else None),
                       "URL": url})
    output = pd.DataFrame(output)

    output["is_subcat"] = output.apply(lambda my_row:
                                       True
                                       if 'kids-onesies' in my_row['taxo2'].lower() or
                                          '3-for-2-kids-clothing' in my_row['taxo2'].lower() or
                                          'easy-dressing' in my_row['taxo2'].lower() or
                                          'new-in-kids-clothing' in my_row['taxo2'].lower() or
                                          'character' in my_row['taxo2'].lower() or
                                          'new-lower-prices' in my_row['taxo2'].lower() or
                                          'easy-dressing-clothing-for-men' in my_row['taxo2'].lower() or
                                          'new-in' in my_row['taxo2'].lower() or
                                          'big-and-tall-guide' in my_row['taxo2'].lower() or
                                          'nightwear-and-pyjamas' in my_row['taxo2'].lower() or
                                          'fleece' in my_row['taxo2'].lower() or
                                          'thinsulate' in my_row['taxo2'].lower() or
                                          'linen-shop' in my_row['taxo2'].lower() or
                                          'david-gandy-for-autograph' in my_row['taxo2'].lower() or
                                          'cashmere' in my_row['taxo2'].lower() or
                                          'mands-fa-suit' in my_row['taxo2'].lower() or
                                          'sequencing' in my_row['taxo2'].lower() or
                                          'wool' in my_row['taxo2'].lower() or
                                          'twiggy' in my_row['taxo2'].lower() or
                                          'workwear' in my_row['taxo2'].lower() or
                                          'must-haves' in my_row['taxo2'].lower() or
                                          'merino-wool' in my_row['taxo2'].lower() or
                                          'great-value' in my_row['taxo2'].lower() or
                                          'per-una' in my_row['taxo2'].lower() or
                                          'classic' in my_row['taxo2'].lower() or
                                          'limited-edition' in my_row['taxo2'].lower() or
                                          'petite' in my_row['taxo2'].lower() or
                                          'autograph' in my_row['taxo2'].lower() or
                                          'mands-collection' in my_row['taxo2'].lower() or
                                          'plus-size-clothing' in my_row['taxo2'].lower() or
                                          'linen' in my_row['taxo2'].lower() or
                                          'wedding-guest' in my_row['taxo2'].lower() or
                                          'florals' in my_row['taxo2'].lower() or
                                          'coords' in my_row['taxo2'].lower() or
                                          'core-sequencing' in my_row['taxo2'].lower() or
                                          'rosie-for-autograph-clothing' in my_row['taxo2'].lower() or
                                          'athleisure' in my_row['taxo2'].lower()
                                       else False, axis=1)

    #######################
    output = output.loc[output['is_subcat'] == False].copy()
    output = output.drop(["is_subcat"], axis=1)

    return output


def get_inventory(taxo1: str, taxo2: str, taxo3: str, url: str):
    print("url: {}".format(url))
    i = 1
    products = []
    try:
        while True:
            url_prod = url + "?pageChoice={}".format(i)
            raw_html = simple_get(url_prod)
            html = BeautifulSoup(raw_html, 'html.parser')

            # get number of page
            nb_pages = html.findAll(name="span", attrs={"class": "pagination__page-x-of-y"})
            nb_pages = str(nb_pages[0].contents[1])
            nb_pages = int(re.search('[0-9]+ of ([0-9]+)', nb_pages, re.IGNORECASE).group(1))

            # get highlighted products
            spotlight_node = html.findAll(name="a", attrs={"class": "spotlight__link"})
            for node in spotlight_node:
                try:
                    data = ET.fromstring(str(node))
                    name = ""
                    price = ""

                    url_product = "https://www.marksandspencer.com" + data.attrib["href"]
                    product_id = re.search('/p/([a-zA-Z0-9]+)?', url_product, re.IGNORECASE).group(1)
                    for subnode in data.findall('./*/*/'):
                        if subnode.attrib["class"] == "spotlight__title":
                            name = subnode.text
                        if subnode.attrib["class"] == "spotlight__normalPrice":
                            price = re.search('.([0-9.]+)', subnode.text, re.IGNORECASE).group(1)
                    products.append({"shop": Shop.MS,
                                     "id": product_id,
                                     "reference": None,
                                     "name": name,
                                     "price": price,
                                     "inStock": True,
                                     "taxo1": taxo1,
                                     "taxo2": taxo2,
                                     "taxo3": taxo3,
                                     "url": url_product,
                                     "date": datetime.datetime.now()})
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR,
                              shop=Shop.MS, message="Error spotlight page {} : {} ({})".format(i, node, ex))

            # get products
            products_node = html.findAll(name="a", attrs={"class": "product__link"})
            for node in products_node:
                try:
                    data = ET.fromstring(str(node))
                    name = ""
                    price = ""

                    url_product = "https://www.marksandspencer.com" + data.attrib["href"]
                    product_id = re.search('/p/([a-zA-Z0-9]+)?', url_product, re.IGNORECASE).group(1)
                    for subnode in data.findall("./div[@class='product__details']/"):
                        if subnode.attrib["class"] == "product__title":
                            name = subnode.text
                        if subnode.attrib["class"] == "product__price":
                            if len(subnode) == 0:
                                price = re.search('.([0-9.]+)', subnode.text, re.IGNORECASE).group(1)
                            else:
                                price = re.search('.([0-9.]+)', subnode[0].text, re.IGNORECASE).group(1)
                    products.append(add_in_dictionary(shop=Shop.MS,
                                                      obj_id=product_id,
                                                      reference=None,
                                                      name=name,
                                                      price=price,
                                                      in_stock=True,
                                                      taxo1=taxo1,
                                                      taxo2=taxo2,
                                                      taxo3=taxo3,
                                                      url=url_product))
                except Exception as ex:
                    log_error(level=ErrorLevel.MINOR,
                              shop=Shop.MS, message="Error node page {} : {} ({})".format(i, node, ex))

            i += 1
            if i > nb_pages:
                break
        return pd.DataFrame(products)
    except Exception as ex:
        log_error(level=ErrorLevel.MEDIUM, shop=Shop.MS, message=ex)
    return None


def parse_ms():
    try:
        df_url = get_categories()
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_category, shop=Shop.MS, message=ex)
        return

    try:
        df_list = [get_inventory(taxo1=row["taxo1"],
                                 taxo2=row["taxo2"],
                                 taxo3=row["taxo3"],
                                 url=row["URL"])
                   for index, row in df_url.iterrows()]
    except Exception as ex:
        log_error(level=ErrorLevel.MAJOR_get_inventory, shop=Shop.MS, message=ex)
        return

    df = pd.concat(df_list)
    save_output(shop=Shop.MS, df=df)
