import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_cls_from_module, operate, convert_to_rub, calculate_relevance


class Gfheddhjek:
    INN = 3241004617
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            print(f"hello 3241004617")
        except Exception as error:
            print(error, Gfheddhjek.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        try:
            print("hello item")
        except Exception as e:
            print(e, Gfheddhjek.BASE_URL)
            return None

