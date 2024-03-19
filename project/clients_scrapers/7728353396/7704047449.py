import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import operate, convert_to_rub, get_web
from project.credentials import TIMEOUT


class Kkdhdhkhhm:
    INN = 7704047449
    BASE_URL = "https://stomatorg.ru"
    SEARCH_URL = "https://api.searchbooster.net/api/9ec1c177-2047-4f1c-b1f9-14a4a7fa9c25/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D&client=shop.stomatorg.ru"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        try:
            logging.warning(f"Sent to {Kkdhdhkhhm.BASE_URL}")
            req = await session.get(Kkdhdhkhhm.SEARCH_URL.format(item), ssl=False)
            res = await req.json()
            logging.warning(f"Got from {Kkdhdhkhhm.BASE_URL}")
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkdhdhkhhm.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """
        if Kkdhdhkhhm.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kkdhdhkhhm.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kkdhdhkhhm.BASE_URL}")
            req = await session.get(link)
            doc = await req.text()
            logging.warning(f"Got from {Kkdhdhkhhm.BASE_URL}")
            doc = BeautifulSoup(doc, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find(class_="tabs-list"))
            if not check:
                res = get_web(link, "tabs-list", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            name = operate(lambda: doc.find(class_="row").find("h1").get_text())
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = operate(lambda: doc.find(class_="element-stickyinfo-prices__curprice").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkdhdhkhhm.BASE_URL}")
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Kkdhdhkhhm.search_relevant_items(item, session)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)


if __name__ == '__main__':
    run_test("стул")
