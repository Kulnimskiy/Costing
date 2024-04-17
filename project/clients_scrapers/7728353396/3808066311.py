import asyncio
import logging
import aiohttp
from typing import Union
from bs4 import BeautifulSoup
from project.helpers import OperationalTools, Browser
from project.managers import UrlManager, PriceManager


class Gldldjjgee:
    INN = 3808066311
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession) -> Union[list, None]:
        """Get a list of relevant items from the competitor's website"""

        check_cls_tag = "TAG TO LOOK FOR ..."

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            """ Looks for a check tag on the page to varify that it's the right page
                document.find(id="catalog-products").find_all(class_=check_cls_tag) """
            pass

        @OperationalTools.operate
        def get_catalog(document: BeautifulSoup):
            """ Gets all the items in the search
                document.find(id="catalog-products").find_all(class_="item") """
            pass

        @OperationalTools.operate
        def get_name(item_in_catalog: BeautifulSoup):
            pass

        @OperationalTools.operate
        def get_price(item_in_catalog: BeautifulSoup):
            """ Returns the price of the item
            There often are old and new prices. Get the NEW one
            Change the type of the price into the right format with PriceManager(price_raw).check() """
            pass

        @OperationalTools.operate
        def get_link(item_in_catalog: BeautifulSoup):
            """ Change the format of the link with the UrlManager(link_raw).check()"""
            pass

        # The algorithm of the search is implemented here. Usually it doesn't change
        try:
            logging.warning(f"Sent to " + Gldldjjgee.BASE_URL)
            req = await session.get(Gldldjjgee.SEARCH_URL.format(item), ssl=False)
            res = await req.text()
            logging.warning(f"Got from " + Gldldjjgee.BASE_URL)
            doc = BeautifulSoup(res, "html.parser")

            # check if the page is loaded correctly. If not, try getting it through the browser
            check = get_check(doc)
            if not check:
                logging.warning(f"BROWSER IS WORKING IN " + Gldldjjgee.BASE_URL)
                res = Browser(Gldldjjgee.SEARCH_URL.format(item)).get_page(cls_wait_tag=check_cls_tag)
                doc = BeautifulSoup(res, "html.parser")

            # get the list of items from the page
            items_found = get_catalog(doc)
            if not items_found:
                logging.warning(f"There are no items in " + Gldldjjgee.BASE_URL)
                return None

            items_lst = []
            for item in items_found:
                # give it the path to the name
                name = get_name(item)
                if not name:
                    logging.warning(f"THERE IS NO NAME. ITEM HAS BEEN SKIPPED")
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
            logging.warning("ERROR: {error} IN: " + Gldldjjgee.BASE_URL)
            return None

    @staticmethod
    async def get_item_info(link: str, session: aiohttp.ClientSession) -> Union[dict, None]:
        """ Get the name, price and link of a competitor's product via the provided web page """

        check_cls_tag = "TAG TO LOOK FOR ..."

        @OperationalTools.operate
        def get_check(document: BeautifulSoup):
            """ checks if the page loads correctly and that is the right page to get the info from """
            pass

        @OperationalTools.operate
        def get_name(document: BeautifulSoup):
            pass

        @OperationalTools.operate
        def get_price(document: BeautifulSoup):
            """ Returns the price of the item
            There often are old and new prices. Get the NEW one
            Change the type of the price into the right format with PriceManager(price_raw).check() """
            pass


        # The algorithm of the search is implemented here. USUALLY IT DOESN'T CHANGE
        if Gldldjjgee.BASE_URL not in link:
            logging.warning(f"WRONG LINK PROVIDED FOR " + Gldldjjgee.BASE_URL)
            return None
        try:
            logging.warning(f"Sent to " + Gldldjjgee.BASE_URL)
            req = await session.get(link, ssl=False)
            res = await req.text()
            logging.warning(f"Got from " + Gldldjjgee.BASE_URL)
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
            logging.warning("ERROR: {error} IN: " + Gldldjjgee.BASE_URL)
            return None


async def test_search(item, link=None):
    async with aiohttp.ClientSession() as session:
        result = await Gldldjjgee.search_relevant_items(item, session)  # link[1] is the url of the item
        result_link = await Gldldjjgee.get_item_info(link, session) if link else None
        return result, result_link


def run_test(item, link):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(item, link))
    print(results)


if __name__ == '__main__':
    run_test("chair", "")