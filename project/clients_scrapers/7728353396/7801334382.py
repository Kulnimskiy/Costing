import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from project.wreckage.helpers import operate, get_web, check_price
from project.credentials import TIMEOUT


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
    async def get_item_info(link: str, session):
        if Kldegghglf.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kldegghglf.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kldegghglf.BASE_URL}")
            req = await session.get(link)
            doc = await req.text()
            logging.warning(f"Got from {Kldegghglf.BASE_URL}")
            doc = BeautifulSoup(doc, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find(class_="h2 text-center content-title content-title-copy-parent"))
            if not check:
                res = get_web(link, "h2 text-center content-title content-title-copy-parent", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            name = operate(lambda: doc.find(class_="h2 text-center content-title content-title-copy-parent").find(
                "h1").get_text())
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = operate(lambda: doc.find(class_="autocalc-product-price").get_text())
            price = check_price(price)
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            print(error, Kldegghglf.BASE_URL)
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Kldegghglf.search_relevant_items(item, session)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)


if __name__ == '__main__':
    run_test("стул")
