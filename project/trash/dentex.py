import requests
from bs4 import BeautifulSoup


class Dentex:
    BASE_URL = "https://dentex.ru"

    @staticmethod
    def search_relevant_items(item):
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
                found_items.append({"name": name, "price": price, "link": link})
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
            return {"name": name, "price": price_int, "link": link}
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
    # item = "стул"
    # for g in Dentex.search_relevant_items(item):
    #     print(g)

    item = "https://dentex.ru/catalog/dental-equipment/dental-motor-handpiece/turbines-handpieces/alegra-te-95-rm/"
    print(Dentex.get_item_info(item))
