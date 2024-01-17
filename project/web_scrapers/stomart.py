from bs4 import BeautifulSoup
import requests
import asyncio


class Stomshop:
    BASE_URL = "https://stomshop.pro"

    @staticmethod
    async def search_relevant_items(item):
        try:
            base_url = f"https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={item}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"
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
        if Stomshop.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            name = operate(
                lambda: doc.find(class_="h2 text-center content-title content-title-copy-parent").find(
                    "h1").get_text())

            # when there is no such item
            if not name:
                print("There is no items")
                return None

            price = operate(lambda: doc.find(class_="autocalc-product-price").get_text())
            price = operate(lambda: int("".join([i for i in price if i.isdigit()])))
            return {"name": name, "price": price, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


class Stomatorg:
    BASE_URL = "https://shop.stomatorg.ru"

    @staticmethod
    async def search_relevant_items(item):
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
            return {"name": name, "price": price, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None


class Dentikom:
    BASE_URL = "https://dentikom.ru"

    @staticmethod
    async def search_relevant_items(item):
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
                link = operate(lambda: Dentikom.BASE_URL + str(thing.find(class_="name")["href"]).strip())
                found_items.append({"name": name, "price": price, "url": link})
            return found_items
        except (requests.exceptions.RequestException, AttributeError) as e:
            print(e)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Dentikom.BASE_URL not in link:
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


class Dentex:
    BASE_URL = "https://dentex.ru"

    @staticmethod
    async def search_relevant_items(item):
        if not item:
            return None
        try:
            base_url = f"https://dentex.ru/search/?q={item}&area=everywhere&s="
            req = requests.get(base_url).text
            doc = BeautifulSoup(req, "html.parser")
            catalog = doc.find("div", class_="short-search")
            items = catalog.find_all("div", class_="item-mini")
            found_items = []
            for thing in items:
                name = operate(lambda: str(thing.find("a", class_="cover-link")["title"]))

                # get the new price if there are 2 of them
                price = operate(lambda: str(thing.find("div", class_="price").text))
                price_int = Dentex.price_format(price)
                link = operate(lambda: Dentex.BASE_URL + str(thing.find("a", class_="cover-link")["href"]))
                found_items.append({"name": name, "price": price, "url": link})
            return found_items
        except (requests.exceptions.RequestException, AttributeError) as e:
            print(e)
            return None

    @staticmethod
    def get_item_info(link: str):
        if Dentex.BASE_URL not in link:
            print("Wrong link")
            return None
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            page = doc.find(class_="item-head")
            if not page:
                return None

            name = operate(lambda: page.find("h1").get_text())
            # when there is no such item
            if not name:
                print("There is no items")
                return None
            price = operate(lambda: page.find(class_="price").find(class_="currency").text)
            price_int = Dentex.price_format(price)
            return {"name": name, "price": price_int, "url": link}
        except (requests.exceptions.RequestException, AttributeError, ValueError) as e:
            print(e)
            return None

    @staticmethod
    def price_format(price):
        """converts the price into the right currency and makes it into an int"""
        price_int = operate(lambda: int("".join([i for i in price if i.isdigit()])))
        if "€" in price.lower():
            price_int = convert_to_rub(price_int, "EUR")
        elif "$" in price.lower():
            price_int = convert_to_rub(price_int, "USD")
        elif "руб" not in price.lower():  # in case there are other currencies
            price_int = None
        return price_int


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


def convert_to_rub(amount: (int, float), currency: str):
    """convert currencies into Russian Ruble """
    currency = currency.strip().upper()
    try:
        data = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()
        currency_rate = float(data["rates"][f"{currency}"])
        return int(amount / currency_rate)
    except (KeyError, AttributeError, requests.exceptions.RequestException) as e:
        print(e)
        return None


if __name__ == "__main__":
    item = "стул"



    # asyncio.run(main())
