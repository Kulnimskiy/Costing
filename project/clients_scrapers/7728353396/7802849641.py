import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class Kldflhmjhe:
    INN = 7802849641
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            print(f"hello 7802849641")
        except Exception as error:
            print(error, Kldflhmjhe.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        try:
            print("hello item")
        except Exception as e:
            print(e, Kldflhmjhe.BASE_URL)
            return None

