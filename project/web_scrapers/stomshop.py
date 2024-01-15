from bs4 import BeautifulSoup
import requests


class Stomshop:

    def __init__(self, item):
        self.item = item
        self.items = self.search_info()

    def search_info(self):
        try:
            base_url = f"https://api4.searchbooster.io/api/12d02e18-b322-4cd6-9904-56712fb66827/search?query={self.item}&skip=0&limit=24&groupByCategories=%7B%22active%22%3Atrue%2C%22size%22%3A10%2C%22skip%22%3A0%7D"
            req = requests.get(base_url).json()
            return req
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


if __name__ == "__main__":
    item = "стул"
    search_json = Stomshop(item).items
    for offer in search_json["offers"]:
        try:
            name = offer["name"]
        except Exception:
            name = None
        try:
            price = offer["price"]
        except Exception:
            price = None
        try:
            url = offer["url"]
        except Exception:
            url = None
        print(name, price, url)
