import re
import requests
from bs4 import BeautifulSoup
from project.helpers import operate
import logging


class Company:
    def __init__(self, inn):
        self.inn = inn
        self.page = self.get_info_page()


    def get_info_page(self):
        url = f"https://checko.ru/search?query={self.inn}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            doc = BeautifulSoup(response.text, "html.parser")

            # Check if company not found
            not_found = doc.find(
                class_="mt-4",
                string="Увы, мы не смогли ничего найти по вашему запросу."
            )

            if not_found:
                logging.warning(f"Company not found for INN: {self.inn}")
                return None

            return doc

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for INN {self.inn}: {e}")
            return None

    def get_full_info(self):
        def look(info):
            try:
                return self.page.find(
                    string=re.compile(f".*\{info}.*")
                ).parent.next_sibling.next_sibling.text

            except Exception as e:
                return None

        if not self.page:
            return {
                "inn": self.inn,
                "website": "",
                "organization": "",
                "ogrn": self.inn,
                "registration_date": "",
                "sphere": "",
                "address": "",
                "workers_number": 0,
                "ceo": "",
            }

        company_info = {
            "inn": self.inn,
            "website": operate(look, "Веб-сайт"),
            "organization": operate(
                lambda: self.page.find("h1", class_="organization-name").text
            ),
            "ogrn": operate(lambda: self.page.find(id="copy-ogrn").text),
            "registration_date": DateFormat(operate(look, "Дата регистрации")),
            "sphere": operate(look, "Вид деятельности"),
            "address": operate(look, "Юридический адрес"),
            "workers_number": operate(
                lambda info: look(info).split()[0],
                "Среднесписочная численность работников",
            ),
            "ceo": operate(lambda: self.page.find("img", width="92")["title"]),
        }
        return company_info


class DateFormat:
    def __init__(self, date):
        self.date = date

    def __repr__(self):
        return self.__format_date(self.date)

    @staticmethod
    def __format_date(date: str):
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
                "декабря": "12",
            }
            date = date.split()
            day = date[0]
            month = date[1]
            year = date[2]
            month = months[month]
            return "-".join([i.strip() for i in [day, month, year]])
        except (ValueError, KeyError, AttributeError, IndexError) as e:
            logging.warning(e)
            return None


if __name__ == "__main__":
    print(DateFormat("17 февраля 2011 фвыафыва"))
    inn = 4704041900
    AGV = Company(inn)
    print(AGV.get_full_info())
