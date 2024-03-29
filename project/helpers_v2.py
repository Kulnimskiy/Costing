import re
import sys
import time
import decimal
import logging
import inspect
from typing import Union
import requests
import validators
import importlib.util
from bs4 import BeautifulSoup
from datetime import datetime
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from project.interfaces import Manager, Hasher





class LoginManager(Manager):
    def __init__(self, login: str):
        self._login = login

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        self._login = value.strip()

    def check(self) -> Union[str, None]:
        """ Checks if the email is valid and returns None if It is not """
        no_space_req = all(not symbol.isspace() for symbol in self.login)
        length_req = len(self.login) >= 3
        if all([self.login, no_space_req, length_req]):
            return self.login
        return None


class PasswordManager(Manager):
    @staticmethod
    def check(password: str) -> Union[str, bool]:
        """The password of 6 char lengths has to have digits and alpha char of lower and upper case with no space"""

        password = str(password).strip()
        length_req = len(password) >= 6
        number_req = any(symbol.isdigit() for symbol in password)
        no_space_req = all(not symbol.isspace() for symbol in password)
        upper_req = any(symbol.isupper() for symbol in password)
        lower_req = any(symbol.islower() for symbol in password)

        # alpha_req = any(symbol.isalpha() for symbol in password)  ## you don't need this as u have the upper and lower req
        if all([no_space_req, length_req, number_req, upper_req, lower_req]):
            return password
        return False


class InnManager(Manager, Hasher):
    @staticmethod
    def check(inn: str) -> Union[str, bool]:
        """for testing purposes the algorithm of checking if the inn exists is not implemented"""
        inn = inn.strip()
        people_len = 10
        company_len = 12
        if len(inn) != people_len and len(inn) != company_len:
            return False
        if any(not digit.isdigit() for digit in inn):
            return False
        return inn

    @staticmethod
    def hash(comp_inn: str):
        comp_inn = str(comp_inn)
        value = ""
        for digit in comp_inn:
            value += chr(100 + int(digit))
        return value.lower().capitalize()

    @staticmethod
    def decode(comp_hash: str):
        value = ""
        for letter in comp_hash:
            value += str(ord(letter.lower()) - 100)
        return value


class PriceManager(Manager):
    @staticmethod
    def check(price: str) -> int:
        """ Returns all the digits from a string as an int if possible
            Used in a class pattern. Do not change the name of the function"""
        try:
            price = int("".join([digit for digit in price if digit.isdigit()]))
            return price
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def convert_to_rub(amount: (int, float), currency: str):
        """convert currencies into Russian Ruble """
        currency = currency.strip().upper()
        try:
            data = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()
            currency_rate = float(data["rates"][f"{currency}"])
            return int(amount / currency_rate)
        except Exception as error:
            print(error)
            return None


class UrlManager(Manager):
    @staticmethod
    def get_link(link):
        if not link:
            return None
        if "http" in link and validators.url(link):
            return link
        else:
            link = "https://" + link
            if validators.url(link):
                return link
        return None

    @staticmethod
    def get_web(link, class_waiting_tag, timeout=50):
        """Get the page using your browser if nothing else is working
        timeout - the time for the program to try to find the target element
        class_waiting_tag - target element to validate that the page has loaded correctly"""
        link = UrlManager.get_link(link)
        if link:
            try:
                chrome_options = Options()

                # Stomart sees when this regime is used and says that we are bots
                chrome_options.add_argument("--headful")
                chrome_options.page_load_strategy = 'none'
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(link)  # This is a dummy website URL
                for i in range(timeout * 2):
                    res = driver.page_source
                    doc = BeautifulSoup(res, "html.parser")
                    if doc.find(class_=class_waiting_tag):
                        print("The page is ready")
                        driver.quit()
                        return res
                    time.sleep(0.5)

                else:
                    driver.quit()
                    print("Error getting a link")
                    print("Loading took too much time!")
            except Exception:
                print("Server Error")
        return None


class ScrapersManager:

    @staticmethod
    def get_cls_from_module(module_name):
        """get all the cls instances within a python file without the imported ones
        use module_name=sys.modules[__name__] to get classes form your file"""

        cls_members = inspect.getmembers(module_name, inspect.isclass)  # get ALL the classes (class_name, class_object)
        # remove the imported classes
        cls_objects = [obj for name, obj in cls_members if obj.__dict__.get("BASE_URL", None)]
        return cls_objects

    @staticmethod
    def get_cls_from_path(path):
        """first you import the module, a list of classes and del the module from the file"""
        try:
            spec = importlib.util.spec_from_file_location("scraper", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["scraper"] = module
            spec.loader.exec_module(module)
            classes = ScrapersManager.get_cls_from_module(module)
            sys.modules.pop('scraper')
            return classes
        except FileNotFoundError as e:
            print(e)
            print(f"There is no such scraper on the path: {path}")
            return None


class OperationalTools:
    @staticmethod
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

    @staticmethod
    def check_int(number: str) -> int:
        if all([symbol.isdigit() for symbol in number]):
            return int(number)
        return 0


class Analysis:
    @staticmethod
    def calculate_relevance(search: str, result: str):
        words = search.split()
        counter = 0
        for word in words:
            if len(word) > 5:
                word = word[1:-2]
            if word.lower() in result.lower():
                counter += 1
        return counter / len(words)

    @staticmethod
    def compare_names(a, b):
        """Used to see if two items relate to each other"""
        item_1 = a.lower()
        item_2 = b.lower()
        models = [word for word in item_1.split() if check_word(word)]
        counter = 0
        for model in models:
            if model in item_2:
                counter += 1
        param3 = counter / len(models) if models else 0
        if param3:
            return param3 * 0.5 + SequenceMatcher(None, a, b).ratio() * 0.3 + calculate_relevance(b, a) * 0.2
        else:
            return SequenceMatcher(None, a, b).ratio() * 0.6 + calculate_relevance(b, a) * 0.4

    @staticmethod
    def format_search_all_result(item, result: dict, competitors, min_price=None, max_price=None, ):
        for r in result:
            if r["price"] is None:
                r["price"] = 0
            for competitor in competitors:
                if competitor.competitor_website in r["url"]:
                    r["competitor"] = competitor.competitor_nickname
                    r["competitor_inn"] = competitor.competitor_inn
        if min_price:
            result = filter(lambda x: x["price"] >= min_price, result)
        if max_price:
            result = filter(lambda x: x["price"] <= max_price, result)
        result = sorted(list(result), key=lambda r: (calculate_relevance(item, r["name"]), r["price"]), reverse=True)
        for r in result:
            if r["price"] == 0:
                r["price"] = "Not selling || Not found"
            else:
                r["price"] = decimal.Decimal(str(r["price"]))
                r["price"] = '{0:,}'.format(r["price"]).replace(',', ' ')
        return result


class ItemModel:
    @staticmethod
    def get_item_model(item_name):
        """to get the model of an item and make it vague to increase the chances to get the result"""
        if item_name:
            models = [word for word in item_name.split() if ItemModel.check_word(word)]
            if len(models) > 3:
                models = [models[i] for i in range(len(models) - int(len(models) * 0.3))]
            if models:
                return " ".join(models)
        return None

    @staticmethod
    def check_word(word):
        digits = any(map(str.isdigit, word))
        latin = any(map(str.isascii, word))
        return any([digits, latin])


class Date:
    """ An object can take a date in the format '5 августа 2014' (года)-optional """
    DATE_FORMAT = "%d.%m.%Y"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    MONTHS = {"января": "01", "февраля": "02", "марта": "03",
              "апреля": "04", "мая": "05", "июня": "06",
              "июля": "07", "августа": "08", "сентября": "09",
              "октября": "10", "ноября": "11", "декабря": "12"}

    def __init__(self, date: str):
        self.date = date

    @property
    def day(self):
        _day = self.__split_date[0]
        if not OperationalTools.check_int(_day):
            return None
        return _day

    @property
    def month(self):
        month = self.__split_date[1]
        if month in Date.MONTHS:
            return Date.MONTHS[month]
        return None

    @property
    def year(self):
        _year = self.__split_date[2]
        if not OperationalTools.check_int(_year):
            return None
        return _year

    def format_date(self):
        form = Date.DATE_FORMAT
        if not all([self.year, self.month, self.day]):
            return None
        date = form.replace("%Y", self.year).replace("%m", self.month).replace("%d", self.day)
        return date

    def format_datetime(self):
        form = Date.DATETIME_FORMAT
        if not all([self.year, self.month, self.day]):
            return None
        date = form.replace("%Y", self.year).replace("%m", self.month).replace("%d", self.day)
        date = date.replace("%H", "00").replace("%M", "00").replace("%S", "00")
        return date

    def __repr__(self):
        return self.format_date()

    @property
    def __split_date(self):
        """ If values"""
        try:
            _split_date = self.date.split()
            if len(_split_date) < 3:
                raise ValueError
            return _split_date
        except ValueError as error:
            logging.warning(error)
            return None


class DateCur(Date):
    """ Works with the current date"""

    @staticmethod
    def cur_date():
        """ Returns the date at the moment in the right format"""
        return datetime.today().strftime(DateCur.DATE_FORMAT)

    @staticmethod
    def cur_datetime() -> str:
        cur_date_str = datetime.now().strftime(DateCur.DATETIME_FORMAT)
        return cur_date_str

    @staticmethod
    def days_passed(date: str) -> int:
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        days_passed = (datetime.now() - date).days
        return days_passed

    @staticmethod
    def minutes_passed(date: str):
        date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        minutes_passed = round((datetime.now() - date).total_seconds() / 60.0)
        return minutes_passed


if __name__ == "__main__":
    EmailManager("sk@agv.ag").message(subject="test", text="Привет!")
    # print(get_link("dentikom/delivery-and-payment/delivery/"))
