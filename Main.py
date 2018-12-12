import sys

sys.path.append('C:/Users/dbrule/PycharmProjects/ClothsRetail')

from Parser.Utils import Shop
from Parser.Asos import parse_asos
from Parser.hm import parse_hm
from Parser.ms import parse_ms
from Parser.Newlook import parse_newlook
from Parser.Primark import parse_primark
from Parser.Zara import parse_zara
import os
os.getcwd()

print("Parse {}".format(Shop.ASOS.value))
parse_asos()

print("Parse {}".format(Shop.HM.value))
parse_hm()

print("Parse {}".format(Shop.MS.value))
parse_ms()

print("Parse {}".format(Shop.NEWLOOK.value))
parse_newlook()

print("Parse {}".format(Shop.PRIMARK.value))
parse_primark()

print("Parse {}".format(Shop.ZARA.value))
parse_zara()
