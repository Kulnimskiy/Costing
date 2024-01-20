import requests
from pprint import pprint
from project.web_scrapers.stomart_sync import Stomatorg, Stomshop, Dentex, Dentikom
import asyncio
import aiohttp
import time
import sys
from project.web_scrapers.stomart_async import get_classes

class FLY:
    pass
table = "s"

print(get_classes(sys.modules[__name__]))


kst = [1,4,6,7,2,5,2,3,4]

print(sorted(kst))
