import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import operate, convert_to_rub, get_web, check_price, get_link
from project.credentials import TIMEOUT


class Kkdmlhkdmg:
    INN = 7709847093
    BASE_URL = "https://dentex.ru"
    SEARCH_URL = "https://dentex.ru/search/?q={}&area=everywhere&s="

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        """Get a list of relevant items from the competitor's website"""
        try:
            logging.warning(f"Sent to {Kkdmlhkdmg.BASE_URL}")
            req = await session.get(Kkdmlhkdmg.SEARCH_URL.format(item))
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")
            logging.warning(f"Got from {Kkdmlhkdmg.BASE_URL}")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = operate(lambda: doc.find("div", class_="short-search"))
            if not check:
                logging.warning(f"BROWSER IS WORKING IN {Kkdmlhkdmg.BASE_URL}")
                res = get_web(Kkdmlhkdmg.SEARCH_URL.format(item), "short-search", TIMEOUT)
                doc = BeautifulSoup(res, "html.parser")

            items_found = operate(lambda: doc.find("div", class_="short-search").find_all("div", class_="item-mini"))
            if not items_found:
                logging.warning(f"There are no items in {Kkdmlhkdmg.BASE_URL}")
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = operate(lambda: str(item.find("a", class_="cover-link")["title"]))
                if not name:
                    logging.warning(f"There is no name. Item has been skipped")
                    continue

                # links are provided with no base url
                link = get_link(operate(lambda: Kkdmlhkdmg.BASE_URL + str(item.find("a", class_="cover-link")["href"])))
                if not link:
                    logging.warning(f"LINK FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: " + name)
                    continue

                # there often are old and new price. Get the new one
                price = operate(lambda: str(item.find("div", class_="price").text))

                # change the type of the price to an int. None if there are no digits.
                price = Kkdmlhkdmg.price_format(price)

                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkdmlhkdmg.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """
        if Kkdmlhkdmg.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kkdmlhkdmg.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kkdmlhkdmg.BASE_URL}")
            req = await session.get(link)
            doc = await req.text()
            logging.warning(f"Got from {Kkdmlhkdmg.BASE_URL}")
            doc = BeautifulSoup(doc, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = doc.find(class_="item-head")
            if not check:
                doc = get_web(link, "recover-password-cabinet-1c")
                doc = BeautifulSoup(doc, "html.parser")

            page = doc.find(class_="item-head")

            name = operate(lambda: page.find("h1").get_text())
            if not name:
                logging.warning(f"There is no items in {link}")
                return None

            price = operate(lambda: page.find(class_="price").find(class_="currency").text)
            price = Kkdmlhkdmg.price_format(price)
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkdmlhkdmg.BASE_URL}")
            return None

    @staticmethod
    def price_format(price):
        """converts the price into the right currency and turnes it into an int"""
        price_int = check_price(price)
        if "€" in price.lower():
            price_int = convert_to_rub(price_int, "EUR")
        elif "$" in price.lower():
            price_int = convert_to_rub(price_int, "USD")
        elif "руб" not in price.lower():  # in case there are other currencies
            price_int = None
        return price_int


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Kkdmlhkdmg.search_relevant_items(item, session)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item))
    print(results)


if __name__ == '__main__':
    run_test("стул")
