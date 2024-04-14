import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import OperationalTools, Browser
from project.managers import UrlManager, PriceManager


class Kkflgiggmj:
    INN = 7728353396
    BASE_URL = "https://www.stomart.ru"
    SEARCH_URL = "https://www.stomart.ru/search/?q={}&send=Y&r=Y"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        """Get a list of relevant items from the competitor's website"""

        check_cls_tag = "productColText"

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            return document.find_all(class_=check_cls_tag)

        @OperationalTools.operate
        def get_catalog(document: BeautifulSoup):
            return document.find_all(class_=check_cls_tag)

        @OperationalTools.operate
        def get_name(item_in_catalog: BeautifulSoup):
            return item_in_catalog.find(class_="name").text

        @OperationalTools.operate
        def get_price(item_in_catalog):
            # there often are old and new price. Get the new one
            price_raw = item.find(class_="price").text
            # change the type of the price to an int. None if there are no digits.
            return PriceManager(price_raw).check()

        @OperationalTools.operate
        def get_link(item_in_catalog: BeautifulSoup):
            link_raw = Kkflgiggmj.BASE_URL + str(item.find(class_="name")["href"])
            return UrlManager(link_raw).check()

        # The algorithm of the search is implemented here
        try:
            logging.warning(f"Sent to {Kkflgiggmj.BASE_URL}")
            req = await session.get(Kkflgiggmj.SEARCH_URL.format(item), ssl=False)
            res = await req.text()
            logging.warning(f"Got from {Kkflgiggmj.BASE_URL}")
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = get_check(doc)
            if not check:
                logging.warning(f"BROWSER IS WORKING IN {Kkflgiggmj.SEARCH_URL.format(item)}")
                res = Browser(Kkflgiggmj.SEARCH_URL.format(item)).get_page(cls_wait_tag=check_cls_tag)
                doc = BeautifulSoup(res, "html.parser")

            # get the list of items from the page
            items_found = get_catalog(doc)
            if not items_found:
                logging.warning(f"There are no items in {Kkflgiggmj.BASE_URL}")
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
            logging.warning(f"ERROR: {error} IN: {Kkflgiggmj.BASE_URL}")
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """

        check_cls_tag = "changeName"

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            """ checks if the page loads correctly and that is the right page to get the info from """
            return document.find(id="catalog-products").find_all(class_=check_cls_tag)

        @OperationalTools.operate
        def get_name(document):
            return document.find("h1", class_="changeName").text

        @OperationalTools.operate
        def get_price(document: BeautifulSoup):
            price_raw = document.find(class_="priceVal").text
            return PriceManager(price_raw).check()

        # The main algorithm is implemented here
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
            logging.warning(f"ERROR: {error} IN: {Kkflgiggmj.BASE_URL}")
            return None


async def test_search(item, link):
    async with aiohttp.ClientSession() as session:
        result = await Kkflgiggmj.search_relevant_items(item, session)  # link[1] is the url of the item
        result_link = await Kkflgiggmj.get_item_info(link, session)
        return result, result_link


def run_test(item, link):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item, link))
    print(results)


if __name__ == '__main__':
    run_test("стул", "https://www.stomart.ru/catalog/ustanovki_i_aksessuary/siger_u200_stomatologicheskaya_ustanovka_1.html")
