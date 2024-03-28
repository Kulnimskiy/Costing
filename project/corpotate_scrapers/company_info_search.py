import re
import requests
from bs4 import BeautifulSoup
from project.helpers import operate, Date


class Company:
    def __init__(self, inn):
        self.inn = inn
        self.page = self.get_info_page()

    def get_info_page(self):
        try:
            _source_url = f"https://checko.ru/search?query={self.inn}"
            req = requests.get(_source_url).text
            doc = BeautifulSoup(req, "html.parser")
            not_successful = doc.body.findAll(class_="mt-4", string='Ничего не найдено')
            if not_successful:
                print("Компания не найдена", not_successful)
                return None
            return doc
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def get_full_info(self):
        def look(info):
            return self.page.find(string=re.compile(f".*\{info}.*")).parent.next_sibling.next_sibling.text

        company_info = {"inn": self.inn,
                        "website": operate(look, "Веб-сайт"),
                        "organization": operate(lambda: self.page.find("h1", class_="organization-name").text),
                        "ogrn": operate(lambda: self.page.find(id="copy-ogrn").text),
                        "registration_date": Date(operate(look, "Дата регистрации")).format_date(),
                        "sphere": operate(look, "Вид деятельности"),
                        "address": operate(look, "Юридический адрес"),
                        "workers_number": operate(lambda info: look(info).split()[0],
                                                  "Среднесписочная численность работников"),
                        "ceo": operate(lambda: self.page.find("img", width="92")["title"])}
        return company_info



if __name__ == "__main__":
    print(Date("17 февраля 2011 фвыафыва"))
    inn = 4704041900
    AGV = Company(inn)
    print(AGV.get_full_info())
