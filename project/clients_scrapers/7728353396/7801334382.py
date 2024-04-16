import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import OperationalTools, Browser
from project.managers import UrlManager, PriceManager


class Kldegghglf:
    INN = 7801334382
    BASE_URL = "https://stomshop.pro"
    SEARCH_URL = "https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        """session object must come from 'async with aiohttp.ClientSession() as session:'
        to make async requests to the api"""
        try:
            logging.warning(f"Sent to {Kldegghglf.BASE_URL}")
            req = await session.get(Kldegghglf.SEARCH_URL.format(item), ssl=False)  # create a request coroutine
            res = await req.json()  # wait till the future value gets replaced with the actual response
            logging.warning(f"Got from {Kldegghglf.BASE_URL}")
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kldegghglf.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """

        check_cls_tag = "h2 text-center content-title content-title-copy-parent"

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            """ checks if the page loads correctly and that is the right page to get the info from """
            return document.find(class_=check_cls_tag)

        @OperationalTools.operate
        def get_name(document):
            return document.find(class_="h2 text-center content-title content-title-copy-parent").find("h1").get_text()

        @OperationalTools.operate
        def get_price(document: BeautifulSoup):
            price_raw = document.find(class_="autocalc-product-price").get_text()
            return PriceManager(price_raw).check()

        # The main algorithm is implemented here
        if Kldegghglf.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kldegghglf.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kldegghglf.BASE_URL}")
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Kldegghglf.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = get_check(doc)
            if not check:
                res = Browser(link).get_page(cls_wait_tag=check_cls_tag)
                doc = BeautifulSoup(res, "html.parser")

            name = get_name(doc)

            if not name:
                logging.warning(f"THERE ARE NO ITEMS IN {link}")
                return None

            price = get_price(doc)
            if not price:
                logging.warning(f"THERE IS NO PRICE IN {link}")

            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kldegghglf.BASE_URL}")
            return None


async def test_search(item, link=None):
    async with aiohttp.ClientSession() as session:
        result = await Kldegghglf.search_relevant_items(item, session)  # link[1] is the url of the item
        result_link = await Kldegghglf.get_item_info(link, session) if link else None
        return result, result_link


def run_test(item, link):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item, link))
    print(results)


if __name__ == '__main__':
    run_test("стул", "https://stomshop.pro/averon-stul-2-1-folk-new")
