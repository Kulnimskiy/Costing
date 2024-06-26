import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import operate, convert_to_rub, get_web, check_price, get_link
from project.credentials import TIMEOUT


class Kkflgiggmj:
    """there was a DDos blocker. Need to actually open a browser to get the info here"""
    INN = 7728353396
    BASE_URL = "https://www.stomart.ru"
    SEARCH_URL = "https://www.stomart.ru/search/?q={}&send=Y&r=Y"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        try:
            req = await session.get(Kkflgiggmj.SEARCH_URL.format(item), ssl=False)
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find_all(class_="productColText"))
            if not check:
                logging.warning(f"BROWSER IS WORKING IN {Kkflgiggmj.SEARCH_URL.format(item)}")
                res = get_web(Kkflgiggmj.SEARCH_URL.format(item), "item", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            # get the list of items from the page
            items_found = operate(lambda: doc.find_all(class_="productColText"))
            if not items_found:
                logging.warning(f"There are no items in {Kkflgiggmj.BASE_URL}")
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = operate(lambda: item.find(class_="name").text)
                if not name:
                    logging.warning(f"There is no name. Item has been skipped")
                    continue

                link = get_link(operate(lambda: Kkflgiggmj.BASE_URL + str(item.find(class_="name")["href"])))
                if not link:
                    logging.warning(f"LINK FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: " + name)
                    continue

                # there often are old and new price. Get the new one
                price = operate(lambda: item.find(class_="price").text)

                # change the type of the price to an int. None if there are no digits.
                price = check_price(price)

                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkflgiggmj.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        if Kkflgiggmj.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kkflgiggmj.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kkflgiggmj.BASE_URL}")
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Kkflgiggmj.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find("h1", class_="changeName"))
            if not check:
                res = get_web(link, "changeName", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            name = operate(lambda: doc.find("h1", class_="changeName").text)
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = operate(lambda: doc.find(class_="priceVal").text)
            price = check_price(price)
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkflgiggmj.BASE_URL}")
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Kkflgiggmj.search_relevant_items(item, session)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)


if __name__ == '__main__':
    run_test("стол")
