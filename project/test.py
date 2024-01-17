import requests
from pprint import pprint
from project.web_scrapers.stomart import Stomatorg, Stomshop, Dentex, Dentikom
import asyncio
import time


async def main():
    start_time = time.time()  # время начала выполнения
    item = "Стул"
    task1 = asyncio.create_task(Dentikom.search_relevant_items(item))
    task2 = asyncio.create_task(Dentex.search_relevant_items(item))
    task3 = asyncio.create_task(Stomshop.search_relevant_items(item))
    task4 = asyncio.create_task(Stomatorg.search_relevant_items(item))
    for g in await task1:
        print(g)
    for i in await task2:
        print(i)
    for i in await task3:
        print(i)
    for i in await task4:
        print(i)


    end_time = time.time()  # время окончания выполнения
    execution_time = end_time - start_time  # вычисляем время выполнения

    print(f"Время выполнения программы: {execution_time} секунд")

asyncio.run(main())

# asyncio.run(main())
