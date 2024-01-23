from .helpers import create_client_folder, hash_inn, unhash_inn





def create_scraper_file(user_login, comp_inn: str):
    try:
        class_name = hash_inn(comp_inn)
        with open(f"./web_scrapers/{user_login}/{comp_inn}.py", "a") as file:
            file.write(f"""import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class {class_name}:
    BASE_URL = ""
    SEARCH_URL = ""
    
    @staticmethod
    async def search_relevant_items(item: str, session: aiohttp.ClientSession):
        try:
            print(f"hello {comp_inn}")
        except Exception as error:
            print(error, {class_name}.BASE_URL)
            return None
       
    @staticmethod
    def get_item_info(link: str):
        try:
            print("hello item")
        except Exception as e:
            print(e, {class_name}.BASE_URL)
            return None

""")
    except FileNotFoundError as error:
        print(error)


if __name__ == "__main__":
    create_client_folder("test")
    create_scraper_file("test", "123456789101")
    print(hash_inn("2345"))
    print(unhash_inn(hash_inn("2345")))
