import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import OperationalTools, Browser
from project.managers import UrlManager


class Efghijmlkmld:
    INN = 123456987980
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        try:
            logging.warning(f"Sent to " + Efghijmlkmld.BASE_URL)
            req = await session.get(Efghijmlkmld.SEARCH_URL.format(item))
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")
            logging.warning(f"Got from " + Efghijmlkmld.BASE_URL)

            # check if the page is loaded correctly. If not, try getting it through the browser
            check =  OperationalTools.operate(lambda: None)
            if not check:
                logging.warning(f"BROWSER IS WORKING IN " + Efghijmlkmld.BASE_URL)
                res = Browser(Efghijmlkmld.SEARCH_URL.format(item)).get_page("CHOOSE_YOUR_CHECK_CLASS")
                doc = BeautifulSoup(res, "html.parser")

            items_found = OperationalTools.operate(lambda: None)
            if not items_found:
                logging.warning(f"There are no items in " + Efghijmlkmld.BASE_URL)
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = OperationalTools.operate(lambda: None)
                if not name:
                    logging.warning(f"There is no name. Item has been skipped")
                    continue

                # links are provided with no base url
                link = UrlManager(OperationalTools.operate(lambda: None)).check()
                if not link:
                    logging.warning(f"LINK FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: {name}")
                    continue

                # there often are old and new price. Get the new one
                price = OperationalTools.operate(lambda: None)

                # change the type of the price to an int. None if there are no digits.
                price = OperationalTools.check_int(price)

                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            logging.warning("ERROR: {error} IN: " + Efghijmlkmld.BASE_URL)
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        if  Efghijmlkmld.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR " + Efghijmlkmld.BASE_URL)
            return None
        try:
            logging.warning(f"Sent to " + Efghijmlkmld.BASE_URL)
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from " + Efghijmlkmld.BASE_URL)
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = OperationalTools.operate(lambda: None)
            if not check:
                res = Browser(link).get_page("CHOOSE_YOUR_CHECK_CLASS")
                doc = BeautifulSoup(res, "html.parser")

            name = OperationalTools.operate(lambda: None)
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = OperationalTools.operate(lambda: doc.find(class_="dpp-price_data__price").find(class_="current-price").text)
            price = OperationalTools.check_int(price)
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning("ERROR: {error} IN: " + Efghijmlkmld.BASE_URL)
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Efghijmlkmld.search_relevant_items(item, session)
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)

