from bs4 import BeautifulSoup
import requests


class Denticom:
    def __init__(self, item):
        self.item = item
        self.relevant_items = self.search_relevant_items()

    def search_relevant_items(self):
        try:
            base_url = f"https://dentikom.ru/catalog/?q={self.item}"
            req = requests.get(base_url).text
            doc = BeautifulSoup(req, "html.parser")
            catalog = doc.find(id="catalog-products")
            items = catalog.find_all(class_="item")
            for thing in items:
                name = str(thing.find(class_="name").text).strip()
                price = str(thing.find(class_="price").text).strip()
                link = str(thing.find(class_="name")["href"]).strip()
                print(name, price, link)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


if __name__ == "__main__":
    item = "стул"
    search_json = Denticom(item).relevant_items
