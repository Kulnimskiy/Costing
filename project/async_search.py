import asyncio
import aiohttp
from project.db_manager import db_get_scr_from_id
from project.helpers import unhash_inn

def get_tasks_items(user_id, item, session, comp_filter=None):
    """Creates a list of tasks to search all items references and
    add the search with each class method to the event loop. You can add tasks either by item or link"""
    classes = db_get_scr_from_id(user_id)
    tasks = []
    if comp_filter:
        for cls in classes:
            if unhash_inn(cls.__name__) in comp_filter:
                tasks.append(asyncio.create_task(cls.search_relevant_items(item, session)))
    else:
        for cls in classes:
            tasks.append(asyncio.create_task(cls.search_relevant_items(item, session)))
    return tasks


def get_tasks_links(user_id, links: list, session):
    """to update prices for all goods in the list asynchronously.
    Gets a list of tuples [(comp1_inn, link), (comp2_inn, link)...]"""
    tasks = []
    for link in links:
        cls = db_get_scr_from_id(user_id, link[0])
        if cls:
            tasks.append(asyncio.create_task(cls.get_item_info(link[1], session)))
        else:
            print(f"Company by inn: {link[0]} is not connected")
    return tasks


async def search_all_items(user_id, item, comp_filter=None):
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks_items(user_id, item, session, comp_filter)
        responses = await asyncio.gather(*tasks)  # wait till all the tasks have brought the result
        results = []
        for response in responses:
            if not response:
                continue
            results.extend(response)
        return results


async def search_all_links(user_id, links: list):
    """gets a list of tuples [(comp1_inn, link), (comp2_inn, link)...] as an argument"""
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks_links(user_id, links, session)
        responses = await asyncio.gather(*tasks)  # wait till all the tasks have brought the result
        results = []
        for response in responses:
            if not response:
                continue
            results.extend([response])
        return results


async def search_link(user_id, comp_inn, link):
    """get info from a link from a particular competitor by his inn"""
    scr = db_get_scr_from_id(user_id, comp_inn)
    if scr:
        async with aiohttp.ClientSession() as session:
            result = await scr.get_item_info(link, session)
            return result
    else:
        return None


async def search_item(user_id, comp_inn, item):
    scr = db_get_scr_from_id(user_id, comp_inn)  # link[0] is the inn of the associated competitor
    if scr:
        async with aiohttp.ClientSession() as session:
            result = await scr.search_relevant_items(item, session)  # link[1] is the url of the item
            return result
    else:
        return None


def run_search_all_items(user_id, item, chosen_comps=None):
    """gets relevant items from all connected competitors"""
    # to get rig of some errors. They happen on Windows
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(search_all_items(user_id, item, chosen_comps))
    return results


def run_search_all_links(user_id, links):
    """gets info from all links associated with items asynchronously.
    links var is a list of tuples [(comp1_inn, link), (comp2_inn, link)...]"""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(search_all_links(user_id, links))
    return results


def run_search_item(user_id, comp_id, item):
    """looks for relevant items in a specified competitor"""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(search_item(user_id, comp_id, item))
    return results


def run_search_link(user_id, comp_id, link):
    """gets info from a link items in a specified competitor"""
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    results = asyncio.run(search_link(user_id, comp_id, link))
    return results


if __name__ == '__main__':
    from project.app import create_app
    from project.helpers import unhash_inn

    app = create_app()
    with app.app_context():
        goods = [("7801334382", "https://stomshop.pro/eighteeth-e-connect-s"),
                 ("7704047449",
                  "https://shop.stomatorg.ru/catalog/slepochnye_materialy_i_aksessuary/slepochnaya_massa_a_silikonovaya_betasil_putty_soft_a60_nabor_2_kh_300_ml_baza_2_kh_50_korrigiruyushch/"),
                 ("6952008773", "https://dentikom.ru/catalog/air-motors/am-25-rm/"),
                 ("7709847093",
                  "https://dentex.ru/catalog/dental-equipment/perio-center/apparat-vector-paro/vector-paro/")]
        found = run_search_link(1, goods[1][0], goods[1][1])
        print(found)
        found = run_search_link(1, goods[3][0], goods[3][1])
        print(found)
