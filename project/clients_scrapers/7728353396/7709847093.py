import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import OperationalTools, Browser
from project.managers import UrlManager, PriceManager


class Kkdmlhkdmg:
    INN = 7709847093
    BASE_URL = "https://dentex.ru"
    SEARCH_URL = "https://dentex.ru/search/?q={}&area=everywhere&s="

    @staticmethod
    def convert_price(price):
        """converts the price into the right currency and turns it into an int """
        price_raw = PriceManager(price)
        if "€" in price.lower():
            return price_raw.convert_to_rub(currency="EUR")
        elif "$" in price.lower():
            return price_raw.convert_to_rub(currency="USD")
        elif "руб" not in price.lower():  # in case there are other currencies
            logging.warning(f"THE PRICE {price} COULD NOT BEEN CONVERTED TO RUB")
            return None
        return price_raw.check()

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        """Get a list of relevant items from the competitor's website"""

        check_cls_tag = "short-search"

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            return document.find("div", class_=check_cls_tag)

        @OperationalTools.operate
        def get_catalog(document: BeautifulSoup):
            return document.find("div", class_="short-search").find_all("div", class_="item-mini")

        @OperationalTools.operate
        def get_name(item_in_catalog: BeautifulSoup):
            return str(item_in_catalog.find("a", class_="cover-link")["title"])

        @OperationalTools.operate
        def get_price(item_in_catalog):
            # there often are old and new price. Get the new one
            price_raw = str(item_in_catalog.find("div", class_="price").text)
            price_raw = price_raw.strip().split("\n")[0]
            # change the type of the price to an int. None if there are no digits
            return Kkdmlhkdmg.convert_price(price_raw)

        @OperationalTools.operate
        def get_link(item_in_catalog: BeautifulSoup):
            link_raw = Kkdmlhkdmg.BASE_URL + str(item_in_catalog.find("a", class_="cover-link")["href"])
            return UrlManager(link_raw).check()

        # The algorithm of the search is implemented here
        try:
            logging.warning(f"Sent to {Kkdmlhkdmg.BASE_URL}")
            req = await session.get(Kkdmlhkdmg.SEARCH_URL.format(item), ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Kkdmlhkdmg.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = get_check(doc)
            if not check:
                logging.warning(f"BROWSER IS WORKING IN {Kkdmlhkdmg.SEARCH_URL.format(item)}")
                res = Browser(Kkdmlhkdmg.SEARCH_URL.format(item)).get_page(cls_wait_tag=check_cls_tag)
                doc = BeautifulSoup(res, "html.parser")

            # get the list of items from the page
            items_found = get_catalog(doc)
            if not items_found:
                logging.warning(f"There are no items in {Kkdmlhkdmg.BASE_URL}")
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = get_name(item)
                if not name:
                    logging.warning(f"There is no name. Item has been skipped")
                    continue

                # links are provided with no base url
                link = get_link(item)
                if not link:
                    logging.warning(f"LINK FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: " + name)
                    continue

                # there often are old and new price. Get the new one
                price = get_price(item)
                if not price:
                    logging.warning(f"PRICE FOR THE ITEM HASN'T BEEN FOUND. ITEM NAME: " + name)
                    continue

                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            logging.warning(f"ERROR: {error} IN: {Kkdmlhkdmg.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """

        check_cls_tag = "item-head"

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            """ checks if the page loads correctly and that is the right page to get the info from """
            return document.find(class_="item-head")

        @OperationalTools.operate
        def get_name(document):
            return document.find(class_="item-head").find("h1").get_text()

        @OperationalTools.operate
        def get_price(document: BeautifulSoup):
            price_raw = document.find(class_="item-head").find(class_="price").find(class_="currency").text
            return Kkdmlhkdmg.convert_price(price_raw)

        # The main algorithm is implemented here
        if Kkdmlhkdmg.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR {Kkdmlhkdmg.BASE_URL}")
            return None
        try:
            logging.warning(f"Sent to {Kkdmlhkdmg.BASE_URL}")
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Kkdmlhkdmg.BASE_URL}")
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
            logging.warning(f"ERROR: {error} IN: {Kkdmlhkdmg.BASE_URL}")
            return None


async def test_search(item, link=None):
    async with aiohttp.ClientSession() as session:
        result = await Kkdmlhkdmg.search_relevant_items(item, session)  # link[1] is the url of the item
        result_link = await Kkdmlhkdmg.get_item_info(link, session) if link else None
        return result, result_link


def run_test(item, link):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item, link))
    print(results)


if __name__ == '__main__':
    run_test("стул", "https://dentex.ru/catalog/dental-equipment/dental-unit/swident/friend-easy-swident/")
