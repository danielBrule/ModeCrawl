import requests
from requests.exceptions import RequestException
from contextlib import closing

DIRECTORY_TMP = "C:/Users/dbrule/PycharmProjects/ClothsRetail/Parser/tmp"


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None)


def simple_get(url):
    try:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
