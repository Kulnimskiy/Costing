from bs4 import BeautifulSoup
import requests


class Stomatorg:
    BASE_URL = "https://shop.stomatorg.ru"

    @staticmethod
    def search_relevant_items(item):
        try:
            base_url = f"https://api.searchbooster.net/api/9ec1c177-2047-4f1c-b1f9-14a4a7fa9c25/search?query={item}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D&client=shop.stomatorg.ru"
            req = requests.get(base_url).json()
            items_lst = []
            for the_offer in req["offers"]:
                found_item = {"name": the_offer.get("name", None),
                              "price": the_offer.get("price", None),
                              "url": the_offer.get("url", None)}
                items_lst.append(found_item)
            return items_lst
        except (requests.exceptions.RequestException, AttributeError) as e:
            print(e)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Stomatorg.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(lambda: doc.find(class_="row").find("h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None

            price = operate(lambda: doc.find(class_="element-stickyinfo-prices__curprice").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "link": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


# function to process the result from parsing
def operate(operation, info=None):
    """function to process the result from parsing"""
    try:
        if info:
            result = operation(info)
            return result
        return operation()
    except (AttributeError, TypeError, ValueError) as e:
        print(e)
        return None


if __name__ == "__main__":
    # search = "стул"
    # for i in Stomshop.search_relevant_items(search):
    #     print(i)

    search = "https://shop.stomatorg.ru/catalog/stomatologicheskie_ustanovki_fengdan/stul_stomatologa_assistenta_mr05/"
    print(Stomatorg.get_item_info(search))
