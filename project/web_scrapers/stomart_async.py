import asyncio
import aiohttp
import inspect
import sys
from time import time
from bs4 import BeautifulSoup
from project.helpers import get_classes


class Stomshop:
    BASE_URL = "https://shop.stomatorg.ru"
    SEARCH_URL = "https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"


class Stomatorg:
    BASE_URL = "https://shop.stomatorg.ru"
    SEARCH_URL = "https://api.searchbooster.net/api/9ec1c177-2047-4f1c-b1f9-14a4a7fa9c25/search?query={}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D&client=shop.stomatorg.ru"


class Dentikom:
    BASE_URL = "https://dentikom.ru"
    SEARCH_URL = "https://dentikom.ru/catalog/?q={}"


class Dentex:
    BASE_URL = "https://dentex.ru"
    SEARCH_URL = "https://dentex.ru/search/?q={}&area=everywhere&s="
    pass


def get_classes_links():
    current_module = sys.modules[__name__]
    clsmembers = inspect.getmembers(current_module, inspect.isclass)
    return [org_class.SEARCH_URL for org_name, org_class in clsmembers]


def get_tasks(session, items):
    """creates a list of all the requests that we need to send asynchronously"""
    tasks = []
    links = get_classes_links()
    for item in items:
        for link in links:
            request_not_sent = session.get(link.format(item), ssl=False)  # it is an awaitable coroutine
            tasks.append(request_not_sent)
            print("task added")
    return tasks


async def search_relevant_items(items):
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session, items)
        responses = await asyncio.gather(
            *tasks)  # creates a list of  multiple task objects adding them to the event loop
        for response in responses:
            print(response)  # You wait until the task is done in the loop
        print("done")


def main():
    start = time()
    items = ["стол", "стул", "резец", "водолазка", "стоматолог"]
    asyncio.run(search_relevant_items(items))
    end = time()
    print("The shit took", end - start, "sec")


res = {"sync": "12.887113809585571",
       "async": "7.395600080490112",
       "async_immediate": ""}
if __name__ == '__main__':
    print(get_classes())
