import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class Jlfmdeekfl:
    INN = 6829011728
    BASE_URL = ""
    SEARCH_URL = ""

    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            print(f"hello 6829011728")
        except Exception as error:
            print(error, Jlfmdeekfl.BASE_URL)
            return None

    @staticmethod
    def get_item_info(link: str):
        try:
            print("hello item")
        except Exception as e:
            print(e, Jlfmdeekfl.BASE_URL)
            return None

