import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class Kkdmlhkdmg:
    INN = 7709847093
    BASE_URL = "https://dentex.ru"
    SEARCH_URL = "https://dentex.ru/search/?q={}&area=everywhere&s="

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            req = await session.get(Kkdmlhkdmg.SEARCH_URL.format(item))
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")

            items_found_raw = doc.find("div", class_="short-search").find_all("div", class_="item-mini")
            items_lst = []
            for item in items_found_raw:
                name = operate(lambda: str(item.find("a", class_="cover-link")["title"]))

                # get the new price if there are 2 of them
                price = operate(lambda: str(item.find("div", class_="price").text))
                price_int = Kkdmlhkdmg.price_format(price)
                link = operate(lambda: Kkdmlhkdmg.BASE_URL + str(item.find("a", class_="cover-link")["href"]))
                items_lst.append({"name": name, "price": price_int, "url": link})
            return items_lst
        except Exception as error:
            print(error, Kkdmlhkdmg.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Kkdmlhkdmg.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            page = doc.find(class_="item-head")
            if not page:
                return None

            name = operate(lambda: page.find("h1").get_text())
            # when there is no such item
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: page.find(class_="price").find(class_="currency").text)
            price_int = Kkdmlhkdmg.price_format(price)
            return {"name": name, "price": price_int, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None

    @staticmethod
    def price_format(price):
        """converts the price into the right currency and turnes it into an int"""
        price_int = operate(lambda: int("".join([i for i in price if i.isdigit()])))
        if "€" in price.lower():
            price_int = convert_to_rub(price_int, "EUR")
        elif "$" in price.lower():
            price_int = convert_to_rub(price_int, "USD")
        elif "руб" not in price.lower():  # in case there are other currencies
            price_int = None
        return price_int

