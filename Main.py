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

now = datetime.datetime.now()

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.JOHNLEWIS, message="start of parsing")
    parse_john_lewis()
    log_error(level=ErrorLevel.TIMING, shop=Shop.JOHNLEWIS, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.JOHNLEWIS, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.ASOS, message="start of parsing")
    parse_asos()
    log_error(level=ErrorLevel.TIMING, shop=Shop.ASOS, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ASOS, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.HM, message="start of parsing")
    parse_hm()
    log_error(level=ErrorLevel.TIMING, shop=Shop.HM, message="endof parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.HM, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.MS, message="start of parsing")
    parse_ms()
    log_error(level=ErrorLevel.TIMING, shop=Shop.MS, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.TIMING, shop=Shop.MS, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.NEWLOOK, message="start of parsing")
    parse_newlook()
    log_error(level=ErrorLevel.TIMING, shop=Shop.NEWLOOK, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.NEWLOOK, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.PRIMARK, message="start of parsing")
    parse_primark()
    log_error(level=ErrorLevel.TIMING, shop=Shop.PRIMARK, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.PRIMARK, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.ZARA, message="start of parsing")
    parse_zara()
    log_error(level=ErrorLevel.TIMING, shop=Shop.ZARA, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.ZARA, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.GAP, message="start of parsing")
    parse_gap()
    log_error(level=ErrorLevel.TIMING, shop=Shop.GAP, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.GAP, message=str(ex))

try:
    log_error(level=ErrorLevel.TIMING, shop=Shop.TKMAXX, message="start of parsing")
    parse_tkmaxx()
    log_error(level=ErrorLevel.TIMING, shop=Shop.TKMAXX, message="end of parsing")
except Exception as ex:
    log_error(level=ErrorLevel.MAJOR, shop=Shop.TKMAXX, message=str(ex))
