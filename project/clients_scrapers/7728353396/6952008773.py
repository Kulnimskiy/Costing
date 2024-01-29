import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_cls_from_module, operate, convert_to_rub, calculate_relevance


class Jmifddlkkg:
    INN = 6952008773
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
            req = await session.get(Jmifddlkkg.SEARCH_URL.format(item), headers=Jmifddlkkg.headers)
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
                link = operate(lambda: Jmifddlkkg.BASE_URL + str(item.find(class_="name")["href"]).strip())
                items_lst.append({"name": name, "price": price, "url": link})
            return items_lst
        except Exception as error:
            print(error, Jmifddlkkg.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Jmifddlkkg.BASE_URL not in link:
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



