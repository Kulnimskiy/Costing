from bs4 import BeautifulSoup
import requests


class Stomshop:
    @staticmethod
    def search_relevant_items(item):
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
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    @staticmethod
    def get_item_info(link: str):
        if "https://stomshop.pro/" not in link:
            print("Wrong link")
            return None
        item = {}
        try:
            req = requests.get(link).text
            doc = BeautifulSoup(req, "html.parser")
            item["name"] = doc.find(class_="h2 text-center content-title content-title-copy-parent").find(
                "h1").get_text()
            price = doc.find(class_="autocalc-product-price").get_text()
            item["price"] = int("".join([i for i in price if i.isdigit()]))
            item["link"] = link
            return item
        except (requests.exceptions.RequestException, AttributeError) as e:
            print(e)
            return None


if __name__ == "__main__":
    search = "https://stomsh.pro/tosi-foshan-tx-414-9c"
    print(Stomshop.get_item_info(search))
