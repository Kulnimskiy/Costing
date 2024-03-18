import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from project.helpers import get_cls_from_module, operate, convert_to_rub, calculate_relevance, get_link


class Kkflgiggmj:
    """there was a DDos blocker. Need to actually open a browser to get the info here"""
    INN = 7728353396
    BASE_URL = "https://www.stomart.ru"
    SEARCH_URL = "https://www.stomart.ru/search/?q={}&send=Y&r=Y"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            # req = await session.get(Kkflgiggmj.SEARCH_URL.format(item), ssl=False, headers=Kkflgiggmj.headers)
            # res = await req.text()
            res = get_link(Kkflgiggmj.SEARCH_URL.format(item))
            doc = BeautifulSoup(res, "html.parser")
            items_found_raw = operate(lambda: doc.find_all(class_="productColText"))
            items_lst = []
            for item in items_found_raw:
                name = operate(lambda: item.find(class_="name").text)
                price = operate(lambda: item.find(class_="price").text)
                price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
                link = operate(lambda: Kkflgiggmj.BASE_URL + str(item.find(class_="name")["href"]))
                items_lst.append({"name": name, "price": price, "url": link})
            for item in items_lst:
                print(item)
            print(f"hello 7728353396")
        except Exception as error:
            print(error, Kkflgiggmj.BASE_URL)
            return None

    @staticmethod
    async def get_item_info(link: str):
        if Kkflgiggmj.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            chrome_options = Options()
            chrome_options.add_argument("---headless")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(link)
            res = driver.page_source
            driver.close()
            doc = BeautifulSoup(res, "html.parser")
            name = operate(lambda: doc.find("h1", class_="changeName").text)
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: doc.find(class_="priceVal").text)
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except Exception as e:
            print(e, link)
            return None


async def test_search(item):
    async with aiohttp.ClientSession() as session:
        result = await Kkflgiggmj.get_item_info(item)  # link[1] is the url of the item
        return result


def run_test(item):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(test_search(
        "https://www.stomart.ru/catalog/ustanovki_i_aksessuary/fedesa_astral_lux_stomatologicheskaya_ustanovka.html"))
    print(results)


if __name__ == '__main__':
    run_test("стул")