import re
import requests
from bs4 import BeautifulSoup


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
                return False
            return doc
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def look(self, info):
        try:
            result = self.page.find(string=re.compile(f".*\{info}.*")).parent.next_sibling.next_sibling.text
            return result
        except AttributeError as e:
            return None

    def get_full_info(self):
        def look(info):
            return self.page.find(string=re.compile(f".*\{info}.*")).parent.next_sibling.next_sibling.text

        def operate(operation, info=None):
            try:
                if info:
                    result = operation(info)
                    return result
                return operation()
            except AttributeError as e:
                return None

        if self.page:
            company_info = {
                "organization": operate(lambda: self.page.find("h1", class_="organization-name").text),
                "ogrn": operate(lambda: self.page.find(id="copy-ogrn").text),
                "registration_date": operate(look, "Дата регистрации"),
                "sphere": operate(look, "Вид деятельности"),
                "address": operate(look, "Юридический адрес"),
                "workers_number": operate(look, "Среднесписочная численность работников")[:-1],
                "CEO": operate(lambda: self.page.find("img", width="92")["title"])
            }
            return company_info


if __name__ == "__main__":
    inn = 7727741653
    AGV = Company(inn)
    print(AGV.get_full_info())
    # print(AGV.get_full_info())
