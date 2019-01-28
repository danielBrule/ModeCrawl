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
from Parser.Gap import parse_gap
from Parser.JohnLewis import parse_john_lewis

try:
    print("Parse {}".format(Shop.JOHNLEWIS.value))
    parse_john_lewis()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.JOHNLEWIS, message=str(ex))

try:
    print("Parse {}".format(Shop.ASOS.value))
    parse_asos()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ASOS, message=str(ex))

try:
    print("Parse {}".format(Shop.HM.value))
    parse_hm()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.HM, message=str(ex))

try:
    print("Parse {}".format(Shop.MS.value))
    parse_ms()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.MS, message=str(ex))

try:
    print("Parse {}".format(Shop.NEWLOOK.value))
    parse_newlook()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.NEWLOOK, message=str(ex))

try:
    print("Parse {}".format(Shop.PRIMARK.value))
    parse_primark()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.PRIMARK, message=str(ex))

try:
    print("Parse {}".format(Shop.ZARA.value))
    parse_zara()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ZARA, message=str(ex))

try:
    print("Parse {}".format(Shop.GAP.value))
    parse_gap()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.GAP, message=str(ex))

try:
    print("Parse {}".format(Shop.TKMAXX.value))
    parse_tkmaxx()
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.TKMAXX, message=str(ex))
