import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class Kkdhdhkhhm:
    INN = 7704047449
    BASE_URL = "https://shop.stomatorg.ru"
    SEARCH_URL = "https://api.searchbooster.net/api/9ec1c177-2047-4f1c-b1f9-14a4a7fa9c25/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D&client=shop.stomatorg.ru"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            req = await session.get(Kkdhdhkhhm.SEARCH_URL.format(item), ssl=False)
            res = await req.json()
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            print(error, Kkdhdhkhhm.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Kkdhdhkhhm.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(lambda: doc.find(class_="row").find("h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None

            price = operate(lambda: doc.find(class_="element-stickyinfo-prices__curprice").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None

