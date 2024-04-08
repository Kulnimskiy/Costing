import logging
import requests
import validators
from typing import Union
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

    def __init__(self, password: str):
        self._password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        self._password = value.strip()

    def check(self) -> Union[str, None]:
        """The password of 6 char lengths has to have digits and alpha char of lower and upper case with no space"""
        length_req = len(self.password) >= 6
        number_req = any(symbol.isdigit() for symbol in self.password)
        no_space_req = all(not symbol.isspace() for symbol in self.password)
        upper_req = any(symbol.isupper() for symbol in self.password)
        lower_req = any(symbol.islower() for symbol in self.password)

        if all([no_space_req, length_req, number_req, upper_req, lower_req]):
            return self.password
        return None


class InnManager(Manager, Hasher):
    INN_PEOPLE_LEN = 10
    INN_ORG_LEN = 12

    def __init__(self, inn: str):
        self._inn = inn

    @property
    def inn(self):
        return self._inn

    @inn.setter
    def inn(self, value: str):
        self._inn = value.strip()

    def check(self) -> str | None:
        """for testing purposes the algorithm of checking if the inn exists is not implemented"""
        inn = self.inn
        if len(inn) not in [InnManager.INN_PEOPLE_LEN, InnManager.INN_ORG_LEN]:
            return None
        if any(not digit.isdigit() for digit in inn):
            return None
        return inn

    def hash(self):
        value = ""
        for digit in self.inn:
            value += chr(100 + int(digit))
        return value.lower().capitalize()

    def decode(self):
        value = ""
        for letter in self.inn:
            value += str(ord(letter.lower()) - 100)
        return value


class PriceManager(Manager):
    """ Gets a price of an item from a string"""

    def __init__(self, price: str):
        self._price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value: str):
        self._price = value.strip()

    def check(self) -> Union[int, None]:
        """ Returns all the digits from a string as an int if possible
            Used in a class pattern. Do not change the name of the function"""
        try:
            price = int("".join([digit for digit in self.price if digit.isdigit()]))
            return price
        except (TypeError, ValueError):
            return None

    def convert_to_rub(self, currency: str = "USD"):
        """convert currencies into Russian Ruble """
        currency = currency.strip().upper()
        price = self.check()
        if price is None:
            return None
        try:
            data = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()
            currency_rate = float(data["rates"][f"{currency}"])
            return int(price / currency_rate)
        except Exception as error:
            logging.warning(f"ERROR: CANNOT CONVERT TO RUB {price} \n{error}")
            return None


class UrlManager(Manager):

    def __init__(self, url: str):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value: str):
        self._url = value.strip()

    def check(self):
        if not self.url:
            return None
        if "http" in self.url and validators.url(self.url):
            return self.url
        else:
            link = "https://" + self.url
            if validators.url(link):
                return link
        return None
