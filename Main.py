import sys

sys.path.append('C:/Users/dbrule/PycharmProjects/ClothsRetail')

from Parser.Utils import *
from Parser.Utils import Shop
from Parser.Asos import parse_asos
from Parser.hm import parse_hm
from Parser.ms import parse_ms
from Parser.Newlook import parse_newlook
from Parser.Primark import parse_primark
from Parser.Zara import parse_zara
from Parser.tkmaxx import parse_tkmaxx

try:
    print("Parse {}".format(Shop.ASOS.value))
    parse_asos()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ASOS, message=ex)

try:
    print("Parse {}".format(Shop.HM.value))
    parse_hm()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.HM, message=ex)

try:
    print("Parse {}".format(Shop.MS.value))
    parse_ms()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.MS, message=ex)

try:
    print("Parse {}".format(Shop.NEWLOOK.value))
    parse_newlook()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.NEWLOOK, message=ex)

try:
    print("Parse {}".format(Shop.PRIMARK.value))
    parse_primark()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.PRIMARK, message=ex)

try:
    print("Parse {}".format(Shop.ZARA.value))
    parse_zara()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ZARA, message=ex)

try:
    print("Parse {}".format(Shop.TKMAXX.value))
    parse_tkmaxx()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.TKMAXX, message=ex)
