import re
from typing import Union

import requests
import logging
from bs4 import BeautifulSoup
from project.helpers_v2 import OperationalTools as Tools, Date
from project.managers import UrlManager


class Company:
    SOURCE = "https://checko.ru/search?query={inn}"

    def __init__(self, inn):
        self.inn = inn
        self.page = self.get_info_page()

    def get_info_page(self):
        try:
            _source_url = Company.SOURCE.format(inn=self.inn)
            req = requests.get(_source_url).text
            doc = BeautifulSoup(req, "html.parser")
            not_successful = doc.body.findAll(class_="mt-4", string='Ничего не найдено')
            if not_successful:
                logging.warning(f"ERROR: COMPANY NOT FOUND \n{not_successful}")
                return None
            return doc
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            raise SystemExit(e)

    def __look(self, info):
        """ Get the main block of info from the SOURCE and look for the keywords"""
        return self.page.find(string=re.compile(f".*\{info}.*")).parent.next_sibling.next_sibling.text

    @Tools.operate
    def get_website(self):
        website = self.__look("Веб-сайт")
        return UrlManager(website).check()

    @Tools.operate
    def get_org(self):
        """ Gets org name"""
        return self.page.find("h1", class_="organization-name").text

    @Tools.operate
    def get_ogrn(self):
        return self.page.find(id="copy-ogrn").text

    @Tools.operate
    def get_reg_date(self):
        """ Gets the unformatted date when the organization was registered"""
        return self.__look("Дата регистрации")

    @Tools.operate
    def get_sphere(self):
        return self.__look("Вид деятельности")

    @Tools.operate
    def get_address(self):
        return self.__look("Юридический адрес")

    @Tools.operate
    def get_workers(self):
        return self.__look("Среднесписочная численность работников").split()[0]

    @Tools.operate
    def get_ceo(self):
        return self.page.find("img", width="92")["title"]

    def get_full_info(self) -> Union[dict, None]:
        """ Get the full company info as a dict """
        if self.page is None:
            logging.warning(f"THE COMPANY DOESN'T EXIST")
            return None

        reg_date = Date(self.get_reg_date()).format_date() if self.get_reg_date() else None
        company_info = {"inn": self.inn,
                        "website": self.get_website(),
                        "organization": self.get_org(),
                        "ogrn": self.get_ogrn(),
                        "registration_date": reg_date,
                        "sphere": self.get_sphere(),
                        "address": self.get_address(),
                        "workers_number": self.get_workers(),
                        "ceo": self.get_ceo()}
        return company_info


if __name__ == "__main__":
    # print(Date("17 февраля 2011 фвыафыва"))
    inn = 4704041900
    AGV = Company(inn)
    print(AGV.get_full_info())
