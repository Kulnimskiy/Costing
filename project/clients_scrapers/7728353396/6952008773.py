import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import operate, convert_to_rub, get_web, check_price, get_link
from project.credentials import TIMEOUT


class Jmifddlkkg:
    INN = 6952008773
    BASE_URL = "https://dentikom.ru"
    SEARCH_URL = "https://dentikom.ru/catalog/?q={}"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        """Get a list of relevant items from the competitor's website"""
        try:
            logging.warning(f"Sent to {Jmifddlkkg.BASE_URL}")
            req = await session.get(Jmifddlkkg.SEARCH_URL.format(item), ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Jmifddlkkg.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find(id="catalog-products").find_all(class_="item"))
            if not check:
                logging.warning(f"BROWSER IS WORKING IN {Jmifddlkkg.BASE_URL}")
                res = get_web(Jmifddlkkg.SEARCH_URL.format(item), "item", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            # get the list of items from the page
            items_found = operate(lambda: doc.find(id="catalog-products").find_all(class_="item"))
            if not items_found:
                logging.warning(f"There are no items in {Jmifddlkkg.BASE_URL}")
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = operate(lambda: str(item.find(class_="name").text).strip())
                if not name:
                    logging.warning(f"There is no name. Item has been skipped")
                    continue

                # links are provided with no base url
                link = get_link(operate(lambda: Jmifddlkkg.BASE_URL + str(item.find(class_="name")["href"]).strip()))
                if not link:
                    logging.warning(f"LINK FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: " + name)
                    continue

                # there often are old and new price. Get the new one
                price = operate(lambda: str(item.find("div", class_="price").text))
                price = operate(lambda: price.strip().split("\n")[0])

                # change the type of the price to an int. None if there are no digits.
                price = check_price(price)

                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Jmifddlkkg.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """
        if Jmifddlkkg.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Jmifddlkkg.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Jmifddlkkg.BASE_URL}")
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Jmifddlkkg.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find(id="catalog-products").find_all(class_="item"))
            if not check:
                res = get_web(link, "detail-product-page in-basket", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            name = operate(lambda: doc.find(class_="detail-product-page in-basket").find("h1").get_text())
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = operate(lambda: doc.find(class_="dpp-price_data__price").find(class_="current-price").text)
            price = check_price(price)
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Jmifddlkkg.BASE_URL}")
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Jmifddlkkg.search_relevant_items(item, session)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)


if __name__ == '__main__':
    run_test("стул")
