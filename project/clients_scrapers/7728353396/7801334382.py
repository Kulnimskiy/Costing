import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_cls_from_module, operate, convert_to_rub, calculate_relevance


class Kldegghglf:
    INN = 7801334382
    BASE_URL = "https://stomshop.pro"
    SEARCH_URL = "https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        """session object must come from 'async with aiohttp.ClientSession() as session:'
        to make async requests to the api"""
        try:
            req = await session.get(Kldegghglf.SEARCH_URL.format(item), ssl=False)  # create a request coroutine
            res = await req.json()  # wait till the future value gets replaced with the actual response
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            print(error, Kldegghglf.BASE_URL)
            return None

    @staticmethod
    async def get_item_info(link: str, session):
        if Kldegghglf.BASE_URL not in link:
            print("Wrong link provided")
            return None
        try:
            print("sent")
            req = await session.get(link)
            doc = await req.text()
            print("got4")
            doc = BeautifulSoup(doc, "html.parser")
            name = operate(
                lambda: doc.find(class_="h2 text-center content-title content-title-copy-parent").find(
                    "h1").get_text())

            # when there is no such item
            if not name:
                print("There are no items")
                return None

            price = operate(lambda: doc.find(class_="autocalc-product-price").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            print(error, Kldegghglf.BASE_URL)
            return None


