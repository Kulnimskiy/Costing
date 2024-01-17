from bs4 import BeautifulSoup
import requests


class Denticom:
    BASE_URL = "https://dentikom.ru"

    @staticmethod
    def search_relevant_items(item):
        if not item:
            return None
        try:
            base_url = f"https://dentikom.ru/catalog/?q={item}"
            req = requests.get(base_url).text
            doc = BeautifulSoup(req, "html.parser")
            catalog = doc.find(id="catalog-products")
            items = catalog.find_all(class_="item")
            found_items = []
            for thing in items:
                name = operate(lambda: str(thing.find(class_="name").text).strip())

                # get the new price if there are 2 of them
                price = operate(lambda: str(thing.find("div", class_="price").text))
                price = operate(lambda: price.strip().split("\n")[0])
                price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
                link = operate(lambda: Denticom.BASE_URL + str(thing.find(class_="name")["href"]).strip())
                found_items.append({"name": name, "price": price, "link": link})
            return found_items
        except (requests.exceptions.RequestException, AttributeError) as e:
            print(e)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Denticom.BASE_URL in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(
                lambda: doc.find(class_="detail-product-page in-basket").find(
                    "h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: doc.find(class_="dpp-price_data__price").find(class_="current-price").text)
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "link": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


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
    item = "https://dentikom.ru/catalog/Dental-Units/6220-surgery/"
    print(Denticom.get_item_info(item))
