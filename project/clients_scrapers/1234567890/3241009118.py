import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import operate, convert_to_rub, calculate_relevance


class Gfheddmeel:
    INN = 3241009118
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            print(f"hello 3241009118")
        except Exception as error:
            print(error, Gfheddmeel.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        try:
            print("hello item")
        except Exception as e:
            print(e, Gfheddmeel.BASE_URL)
            return None

