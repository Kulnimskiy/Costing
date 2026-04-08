import re
import requests
from bs4 import BeautifulSoup
from project.helpers import operate, safe_text, safe_attr
import logging


class Company:
    def __init__(self, inn):
        self.inn = inn
        self.page = self.get_info_page()

    def get_info_page(self):
        url = f"https://checko.ru/search?query={self.inn}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/115.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
        }

        session = requests.Session()
        session.headers.update(headers)

        for _ in range(3):
            try:
                response = session.get(url, timeout=10)
                response.raise_for_status()

                doc = BeautifulSoup(response.text, "html.parser")

                not_found = doc.find(
                    class_="mt-4",
                    string="Увы, мы не смогли ничего найти по вашему запросу."
                )

                if not_found:
                    logging.warning(f"Company not found for INN: {self.inn}")
                    return None

                return doc

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    wait = random.uniform(5, 15)
                    logging.warning(f"429 Too Many Requests, waiting {wait:.1f}s")
                    time.sleep(wait)
                else:
                    logging.error(f"HTTP error for INN {self.inn}: {e}")
                    return None
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed for INN {self.inn}: {e}")
                time.sleep(random.uniform(1, 3))

        logging.error(f"Failed 3 attempts for INN {self.inn}")
        return None

    def get_full_info(self):
        if not self.page:
            return {
                "inn": self.inn,
                "website": None,
                "organization": None,
                "ogrn": self.inn,
                "registration_date": None,
                "sphere": None,
                "address": None,
                "workers_number": 0,
                "ceo": None,
            }

        def look(label):
            """Helper to find a value by label in the page table"""
            try:
                element = self.page.find(string=re.compile(f".*{re.escape(label)}.*"))
                if element and element.parent and element.parent.next_sibling:
                    value = element.parent.next_sibling.next_sibling
                    return safe_text(value)
                return None
            except Exception as e:
                logging.warning(f"look() failed for '{label}': {e}")
                return None

        def safe_workers_number(label):
            val = look(label)
            try:
                return int(val.split()[0]) if val else 0
            except Exception as e:
                logging.warning(f"Parsing workers_number failed: {e}")
                return 0

        company_info = {
            "inn": self.inn,
            "website": operate(look, "Веб-сайт"),
            "organization": safe_text(self.page.find("h1", class_="organization-name")),
            "ogrn": safe_text(self.page.find(id="copy-ogrn")),
            "registration_date": DateFormat(operate(look, "Дата регистрации")),
            "sphere": operate(look, "Вид деятельности"),
            "address": operate(look, "Юридический адрес"),
            "workers_number": safe_workers_number("Среднесписочная численность работников"),
            "ceo": safe_attr(self.page.find("img", width="92"), "title"),
        }

        return company_info

class DateFormat:
    def __init__(self, date_str):
        self.date = self.__format_date(date_str)

    def __str__(self):
        return self.date.isoformat() if self.date else ""

    def __repr__(self):
        return str(self)

    @staticmethod
    def __format_date(date_str: str):
        """Convert a Russian date like '7 июня 2004' to datetime.date"""
        if not date_str:
            return None

        months = {
            "января": 1,
            "февраля": 2,
            "марта": 3,
            "апреля": 4,
            "мая": 5,
            "июня": 6,
            "июля": 7,
            "августа": 8,
            "сентября": 9,
            "октября": 10,
            "ноября": 11,
            "декабря": 12,
        }

        try:
            parts = date_str.strip().split()
            day = int(parts[0])
            month = months[parts[1].lower()]
            year = int(parts[2])
            return date(year, month, day)
        except (ValueError, KeyError, IndexError, AttributeError) as e:
            logging.warning(f"Date parsing failed for '{date_str}': {e}")
            return None


if __name__ == "__main__":
    print(DateFormat("17 февраля 2011 фвыафыва"))
    inn = 4704041900
    AGV = Company(inn)
    print(AGV.get_full_info())
