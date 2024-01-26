import os
from .helpers import hash_inn, unhash_inn


def create_client_folder(user_inn: str):
    # dir_name = hash_inn(user_inn)
    dir_name = str(user_inn)
    parent_path = ".\project\clients_scrapers"
    path = os.path.join(parent_path, dir_name)
    try:
        os.mkdir(path)
    except FileExistsError as error:
        print(error)


def create_scraper_file(user_inn: str, comp_inn: str):
    """returns the path where the scraper has been created"""
    try:
        # user_inn = hash_inn(user_inn)W
        # class_name = hash_inn(comp_inn)
        class_name = hash_inn(comp_inn)
        user_inn = str(user_inn)
        path = f""".\project\clients_scrapers\{user_inn}\{str(comp_inn)}.py"""
        with open(path, "a") as file:
            file.write(f"""import asyncio
import aiohttp
import sys
import time
import requests
from bs4 import BeautifulSoup
from project.helpers import get_classes, operate, convert_to_rub, calculate_relevance


class {class_name}:
    INN = {comp_inn}
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
        return path
    except FileNotFoundError as error:
        print(error)
        return None


def delete_empty_scraper():
    pass


if __name__ == "__main__":
    create_client_folder("test")
    create_scraper_file("test", "123456789101")
    print(hash_inn("2345"))
    print(unhash_inn(hash_inn("2345")))
