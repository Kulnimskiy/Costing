import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_cls_from_module, operate, convert_to_rub, calculate_relevance


class Stomshop:
    BASE_URL = "https://stomshop.pr"
    SEARCH_URL = "https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        """session object must come from 'async with aiohttp.ClientSession() as session:'
        to make async requests to the api"""
        try:
            req = await session.get(Stomshop.SEARCH_URL.format(item), ssl=False)  # create a request coroutine
            res = await req.json()  # wait till the future value gets replaced with the actual response
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            print(error, Stomshop.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Stomshop.BASE_URL not in link:
            print("Wrong link provided")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(
                lambda: doc.find(class_="h2 text-center content-title content-title-copy-parent").find(
                    "h1").get_text())

            # when there is no such item
            if not name:
                print("There are no items")
                return None

            price = operate(lambda: doc.find(class_="autocalc-product-price").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except Exception as error:
            print(error)
            return None
        pass


class Stomatorg:
    BASE_URL = "https://shop.stomatorg.ru"
    SEARCH_URL = "https://api.searchbooster.net/api/9ec1c177-2047-4f1c-b1f9-14a4a7fa9c25/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D&client=shop.stomatorg.ru"

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            req = await session.get(Stomatorg.SEARCH_URL.format(item), ssl=False)
            res = await req.json()
            items_lst = []
            for offer in res["offers"]:
                found_item = {"name": offer.get("name", None),
                              "price": offer.get("price", None),
                              "url": offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except Exception as error:
            print(error, Stomatorg.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Stomatorg.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(lambda: doc.find(class_="row").find("h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None

            price = operate(lambda: doc.find(class_="element-stickyinfo-prices__curprice").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


class Dentikom:
    BASE_URL = "https://dentikom.ru"
    SEARCH_URL = "https://dentikom.ru/catalog/?q={}"
    headers = {"authority": "dentex.ru",
               "method": "GET",
               "path": "/",
               "scheme": "https",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
               "Cache-Control": "max-age=0",
               "Cookie": "_ga=GA1.2.1897268539.1705514640; tmr_lvid=2c8fa6650ca19f62bb743354a630e2eb; tmr_lvidTS=1705514640408; _ym_uid=1705514640929139899; _ym_d=1705514640; BX_USER_ID=653655e16c7a454a83e2b8f7e8f9a029; __lhash_=404c1f2a67e812672473d72c9f9af9ba; _gid=GA1.2.1248177102.1705701000; _ym_isad=1; __js_p_=981,1800,0,0,0; __jhash_=1106; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F120.0.0.0%20Safari%2F537.36; __hash_=ca4ed67e83859115f76a84b315bfd779; PHPSESSID=285c7138f5e1e43b3445b60aa10ea68b; tipclose=0; BITRIX_CONVERSION_CONTEXT_s1=%7B%22ID%22%3A2%2C%22EXPIRE%22%3A1705870740%2C%22UNIQUE%22%3A%5B%22conversion_visit_day%22%5D%7D; _ym_visorc=w; tmr_detect=1%7C1705786022798; _ga_CNKZ8LP81E=GS1.2.1705785984.5.1.1705786022.0.0.0",
               "Referer": "https://dentex.ru/",
               "Sec-Ch-Ua": "Not_A Brand",
               "Sec-Ch-Ua-Mobile": "?0",
               "Sec-Ch-Ua-Platform": "Windows",
               "Sec-Fetch-Dest": "document",
               "Sec-Fetch-Mode": "navigate",
               "Sec-Fetch-Site": "same-origin",
               "Sec-Fetch-User": "?1",
               "Upgrade-Insecure-Requests": "1",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            req = await session.get(Dentikom.SEARCH_URL.format(item), headers=Dentikom.headers)
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")
            items_found_raw = operate(lambda: doc.find(id="catalog-products").find_all(class_="item"))
            items_lst = []
            for item in items_found_raw:
                name = operate(lambda: str(item.find(class_="name").text).strip())

                # there often are old and new price. Get the new one
                price = operate(lambda: str(item.find("div", class_="price").text))
                price = operate(lambda: price.strip().split("\n")[0])

                # change the type of the price to an int
                price = operate(lambda: int("".join([i for i in price if i.isdigit()])))

                # links are provided with no base url
                link = operate(lambda: Dentikom.BASE_URL + str(item.find(class_="name")["href"]).strip())
                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            print(error, Dentikom.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Dentikom.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(
                lambda: doc.find(class_="detail-product-page in-basket").find(
                    "h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: doc.find(class_="dpp-price_data__price").find(class_="current-price").text)
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "link": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


class Dentex:
    BASE_URL = "https://dentex.ru"
    SEARCH_URL = "https://dentex.ru/search/?q={}&area=everywhere&s="

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            req = await session.get(Dentex.SEARCH_URL.format(item))
            res = await req.text()
            doc = BeautifulSoup(res, "html.parser")

            items_found_raw = doc.find("div", class_="short-search").find_all("div", class_="item-mini")
            items_lst = []
            for item in items_found_raw:
                name = operate(lambda: str(item.find("a", class_="cover-link")["title"]))

                # get the new price if there are 2 of them
                price = operate(lambda: str(item.find("div", class_="price").text))
                price_int = Dentex.price_format(price)
                link = operate(lambda: Dentex.BASE_URL + str(item.find("a", class_="cover-link")["href"]))
                items_lst.append({"name": name, "price": price_int, "url": link})
            return items_lst
        except Exception as error:
            print(error, Dentex.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Dentex.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            page = doc.find(class_="item-head")
            if not page:
                return None

            name = operate(lambda: page.find("h1").get_text())
            # when there is no such item
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: page.find(class_="price").find(class_="currency").text)
            price_int = Dentex.price_format(price)
            return {"name": name, "price": price_int, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None

    @staticmethod
    def price_format(price):
        """converts the price into the right currency and turnes it into an int"""
        price_int = operate(lambda: int("".join([i for i in price if i.isdigit()])))
        if "€" in price.lower():
            price_int = convert_to_rub(price_int, "EUR")
        elif "$" in price.lower():
            price_int = convert_to_rub(price_int, "USD")
        elif "руб" not in price.lower():  # in case there are other currencies
            price_int = None
        return price_int


def get_tasks(item, session):
    """Creates a list of tasks to search all items references and
    add the search with each class method to the event loop"""
    classes = get_cls_from_module(sys.modules[__name__])
    tasks = []
    for cls in classes:
        tasks.append(asyncio.create_task(cls.search_relevant_items(item, session)))
    return tasks


async def search_all(item):
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(item, session)
        responses = await asyncio.gather(*tasks)  # wait till all the tasks have brought the result
        results = []
        for response in responses:
            if not response:
                continue
            results.extend(response)
        return results


def run_search_all(item):
    # to get rig of some errors. They happen on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(search_all(item))
    return results


if __name__ == "__main__":
    start = time.time()
    test_results = run_search_all("стул")
    for result in test_results:
        print(result)
    print("Number of relevant items: ", len(test_results))
    end = time.time()
    print("done for", end - start, "sec")
