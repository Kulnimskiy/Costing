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
                return None
            return doc
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def get_full_info(self):
        def look(info):
            return self.page.find(string=re.compile(f".*\{info}.*")).parent.next_sibling.next_sibling.text

        def operate(operation, info=None):
            try:
                if self.page:
                    if info:
                        result = operation(info)
                        return result
                    return operation()
                return None
            except (AttributeError, TypeError) as e:
                print(e)
                return None

        company_info = {
            "website": operate(look, "Веб-сайт"),
            "organization": operate(lambda: self.page.find("h1", class_="organization-name").text),
            "ogrn": operate(lambda: self.page.find(id="copy-ogrn").text),
            "registration_date": Company.format_date(operate(look, "Дата регистрации")),
            "sphere": operate(look, "Вид деятельности"),
            "address": operate(look, "Юридический адрес"),
            "workers_number": operate(lambda info: look(info).split()[0], "Среднесписочная численность работников"),
            "CEO": operate(lambda: self.page.find("img", width="92")["title"])}
        return company_info

    @staticmethod
    def format_date(date: str):
        try:
            months = {
                "января": "01",
                "февраля": "02",
                "марта": "03",
                "апреля": "04",
                "мая": "05",
                "июня": "06",
                "июля": "07",
                "августа": "08",
                "сентября": "09",
                "октября": "10",
                "ноября": "11",
                "декабря": "11"}
            day, month, year, etc = date.split()
            month = months[month]
            return ".".join([i.strip() for i in [day, month, year]])
        except (ValueError, KeyError) as e:
            print(e)
            return None


if __name__ == "__main__":
    print(Company.format_date("17 феврали 2011"))
    inn = 4704041900
    AGV = Company(inn)
    print(AGV.get_full_info())
