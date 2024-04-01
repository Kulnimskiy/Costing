import time
import decimal
import logging
from typing import Union
from datetime import datetime
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from project.managers import UrlManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class OperationalTools:
    @staticmethod
    def operate(operation):
        """function to process the result from parsing"""

        def wrapper(*args, **kwargs):
            try:
                result = operation(*args, **kwargs)
                return result
            except (AttributeError, TypeError, ValueError) as error:
                logging.warning(error)
                return None

        return wrapper

    @staticmethod
    def check_int(number: str) -> int:
        if all([symbol.isdigit() for symbol in number]):
            return int(number)
        return 0


class ItemName:
    """ Works wih item names and gets info out of it"""

    def __init__(self, item_name: str):
        self.item_name = item_name

    def get_model(self) -> Union[str, None]:
        """ Gets the model of an item and makes it vague to increase the chances to get the result"""
        models = [word for word in self.item_name.split() if word.isascii()]
        if len(models) > 3:
            models = [models[i] for i in range(len(models) - int(len(models) * 0.3))]
        if models:
            return " ".join(models)
        return None

    def relevance(self, another_item: str):
        """ Give the possibility of 2 items being the same ones with slightly different names"""
        words = self.same_words(another_item)
        model = self.same_model(another_item)
        sequence = self.same_sequence(another_item)
        if model is None:
            return sequence * 0.7 + words * 0.3  # weights of each param have been gotten from practice and stat results
        return model * 0.5 + sequence * 0.3 + words * 0.2

    def same_words(self, another_item: str) -> float:
        """ Gets the percentage of the same words in the two items names """
        item_words = self.item_name.split()
        counter = 0
        for word in item_words:
            if len(word) > 5:
                word = word[1:-2]
            if word.lower() in another_item.lower():
                counter += 1
        return float(counter / len(item_words))

    def same_model(self, another_item) -> Union[float, None]:
        """ Gets the percentage of the same words in the two items models """
        model = self.get_model()
        if model is None:
            return None
        model_words = model.split()
        counter = 0
        for model in model_words:
            if model.lower() in another_item.lower():
                counter += 1
        return counter / len(model_words)

    def same_sequence(self, another_item: str) -> float:
        """ Gets the percentage of the same sequence of words in the two items names """

        item_a = self.item_name.lower()
        item_b = another_item.lower()
        return SequenceMatcher(None, item_a, item_b).ratio()


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
        print(self.date)
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


class Browser(UrlManager):
    """ Opens pages in Chrome and sets page loading strategies like 'none', 'eager' and 'normal'
        Can open browser in the headless regime"""

    def __init__(self, url: str, headless: bool = False, strategy: str = 'none'):
        super().__init__(url=url)
        self.driver = self.__set_up(headless, strategy)

    @staticmethod
    def __set_up(headless: bool, strategy: str):
        """ Note that some websites don't give a valid page in a headless regime"""
        options = Options()
        if headless:
            options.add_argument("--headless")
        if strategy in ["none", "eager", "normal"]:
            options.page_load_strategy = strategy
        return webdriver.Chrome(options=options)

    @staticmethod
    def __get_tag(page, tag: str) -> bool:
        doc = BeautifulSoup(page, "html.parser")
        if doc.find(class_=tag):
            logging.warning(f"INFO: THE PAGE IS VALID. TAG {tag} IS FOUND")
            return True
        return False

    def get_page(self, cls_wait_tag: str = None, attempts: int = 30, delay: float = 0.5):
        """ Get the page using your browser if nothing else is working. Args: cls_wait_tag - target element to validate
        that the page has loaded correctly, attempts - number of tries between attempts to find a tag, delay - seconds
        between attempts """

        url = self.check()  # get the valid url
        driver = self.driver
        try:
            driver.get(url)
            if cls_wait_tag is None:
                return driver.page_source
            for i in range(attempts):
                page = driver.page_source
                if self.__get_tag(page, cls_wait_tag):
                    driver.quit()
                    return page
                time.sleep(delay)
            else:
                driver.quit()
                logging.warning(f"ERROR: TAG {cls_wait_tag} CANNOT BE FOUND OR LOADING TAKES TO MUCH TIME")
        except Exception as error:
            logging.warning(f"ERROR: CANNOT GET PAGE {url} \n{error}")
        return None


class ResultFormats:
    """ NEED TO GET RID OF THIS MESS """

    @staticmethod
    def search_all_result(item, result: dict, competitors, min_price=None, max_price=None, ):
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
        result = sorted(list(result), key=lambda r: (ItemName(item).relevance(r["name"]), r["price"]), reverse=True)
        for r in result:
            if r["price"] == 0:
                r["price"] = "Not selling || Not found"
            else:
                r["price"] = decimal.Decimal(str(r["price"]))
                r["price"] = '{0:,}'.format(r["price"]).replace(',', ' ')
        return result


if __name__ == '__main__':
    print(Browser("dasfsdfsdf.ru").get_page("L3eUgb"))
