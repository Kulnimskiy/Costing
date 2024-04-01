import logging
from typing import Union

from sqlalchemy import func
from project import db
from project.models import Companies, Competitors, Scrapers, ItemsRecords, UsersItems, ItemsConnections, User
from project.corpotate_scrapers.search_company import Company
from project.systems import ScraperSystem
from project.helpers import get_cls_from_path, get_cur_date, get_link
from project.managers import UrlManager
from helpers_v2 import DateCur
from project import async_search

DAYS_BEFORE_RELOAD = 3  # Number of days to update the info about a company
ITEMS_UPDATE = 1  # Number of days to add new records of the item


class CompanyDB:
    model = Companies

    def __init__(self, inn):
        self.inn = inn

    def get(self) -> Union[Companies, None]:
        """ Get the company info from the db """
        company = self.model.query.filter_by(_inn=self.inn).first()
        if company:
            return company
        return None

    def create(self) -> bool:
        """ Creates a company from its inn and adds it to the db """

        if self.get():  # Check if the company already exists
            return False

        company_info = Company(self.inn).get_full_info()
        if company_info is None:
            logging.warning(f"THE COMPANY {self.inn} WASN'T CREATED")
            return False

        new_company = Companies(_inn=company_info["inn"],
                                website=company_info["website"],
                                organization=company_info["organization"],
                                ogrn=company_info["ogrn"],
                                registration_date=company_info["registration_date"],
                                sphere=company_info["sphere"],
                                address=company_info["address"],
                                workers_number=company_info["workers_number"],
                                ceo=company_info["ceo"],
                                info_loading_date=DateCur.cur_date())
        db.session.add(new_company)
        db.session.commit()
        return True

    def _update(self):
        """ Updates the info about the company """
        company = self.get()
        if not company:  # Check if the company already exists
            return False

        company_info = Company(self.inn).get_full_info()
        company.inn = company_info["inn"]
        company.organization = company_info["organization"]
        company.ogrn = company_info["ogrn"]
        company.registration_date = company_info["registration_date"]
        company.sphere = company_info["sphere"]
        company.address = company_info["address"]
        company.workers_number = company_info["workers_number"]
        company.ceo = company_info["ceo"]
        company.info_loading_date = DateCur.cur_date()

        # if there is new info about a website, we change it
        web = company_info["website"]
        if web and company.website != UrlManager(web).check():
            company.website = UrlManager(web).check()
        db.session.commit()
        return True

    def load(self):
        """ Gets data using from db or from the web if it's been more than DAYS_BEFORE_RELOAD days"""
        company = self.get()
        if company:
            days_passed = DateCur.days_passed(company.info_loading_date)
            if days_passed < DAYS_BEFORE_RELOAD:  # reload the company info every other day
                return company
            if self._update():
                company_updated = self.get()
                return company_updated
            logging.warning(f"THE COMPANY {self.inn} WASN'T UPDATED!")
            return company

        if self.create():  # if the company hasn't been added to the db
            return self.get()
        return None


class CompetitorDB:
    """ Manages competitors in th db. cp - competitor """
    CONNECTION_STATUS = ["disconnected", "connected", "requested"]

    def __init__(self, user_id, cp_inn):
        self.user_id = user_id
        self.cp_inn = cp_inn

    def get(self):
        return Competitors.query.filter_by(user_id=self.user_id, competitor_inn=self.cp_inn).first()

    @staticmethod
    def get_all(user_id, connection_status=""):
        """connection status can be 'disconnected', 'connected','requested'. Only those are in the db"""
        if connection_status in CompetitorDB.CONNECTION_STATUS:
            return Competitors.query.filter_by(user_id=user_id, connection_status=connection_status).all()
        return Competitors.query.filter_by(user_id=user_id).all()

    def create(self, cp_nickname=None, website=None):
        """ Creates a competitor and loads him to the db """
        cp = self.get()
        if cp:
            logging.warning(f"COMPETITOR {self.cp_inn} IS ALREADY ADDED TO USER {self.user_id}")
            return False
        cp = CompanyDB(self.cp_inn).load()
        if not cp:
            logging.warning(f"UNABLE TO GET {self.cp_inn} COMPETITOR FROM THE WEB")
            return False

        nickname = cp_nickname if cp_nickname else cp.organization  # let the user customize naming
        web = UrlManager(website).check()  # check if the website the user has given is valid
        website = web if web else cp.website  # let the user get the needed web if not possible to get from the source
        new_competitor = Competitors(user_id=self.user_id,
                                     competitor_inn=self.cp_inn,
                                     competitor_nickname=nickname,
                                     competitor_website=website)
        db.session.add(new_competitor)
        db.session.commit()

        return True

    def update_status(self, new_status="requested"):
        """ Change the status of the competitor to the new one """
        if new_status not in CompetitorDB.CONNECTION_STATUS:
            logging.warning(f"THE CONNECTION STATUS {new_status} IS NOT SUPPORTED")
            return False

        cp = self.get()
        if not cp:
            logging.warning(f"THE COMPANY {self.cp_inn} IS NOT A COMPETITOR FOR USER: {self.user_id}")
            return False

        cp.connection_status = new_status
        db.session.commit()
        return True

    def delete(self):
        cp = self.get()
        if not cp:
            logging.warning(f"THE COMPANY {self.cp_inn} IS NOT A COMPETITOR FOR USER: {self.user_id}")
            return False

        # save the scraper path to know if it's used anywhere
        scr_path = ScraperDB(self.user_id, self.cp_inn).get_path()

        db.session.delete(cp)
        db.session.commit()

        scr_times_used = len(Competitors.query.filter_by(competitor_inn=self.cp_inn).all())
        if scr_times_used == 0:
            ScraperSystem(self.user_id, self.cp_inn).delete(scr_path)
            logging.warning(f"SCRAPER FOR {self.cp_inn} IS NO LONGER NEEDED!")
        return True


class ScraperDB:
    def __init__(self, user_id, cp_inn):
        self.user_id = user_id
        self.cp_inn = cp_inn

    def get(self):
        scr = Scrapers.query.filter_by(company_inn=self.cp_inn).first()
        if scr:
            return scr
        return None

    def get_path(self):
        scr = self.get()
        if scr:
            return scr.scraper_path
        return None

    @staticmethod
    def get_all(user_id):
        """ Gets all scrapers for a user """
        cps = CompetitorDB.get_all(user_id)
        inns_ = [cp.competitor_inn for cp in cps]
        scrs = Scrapers.query.filter(Scrapers.company_inn.in_(inns_)).all()
        return scrs

    def get_cls(self):
        """ Gets the scraper class from the according file """
        cp = CompetitorDB(self.user_id, self.cp_inn).get()
        if not cp or cp.connection_status != CompetitorDB.CONNECTION_STATUS[1]:  # if the competitor is not connected
            logging.warning(f"THE COMPETITOR {self.cp_inn} IS NOT CONNECTED!")
            return None
        scr_path = self.get_path()
        cls = ScraperSystem.get_from_path(scr_path)
        return cls

    @staticmethod
    def get_cls_all(user_id):
        """ Gets all the scraper classes for the according user """
        cps = CompetitorDB.get_all(user_id, CompetitorDB.CONNECTION_STATUS[1])
        inns_ = [cp.competitor_inn for cp in cps]
        scrs = Scrapers.query.filter(Scrapers.company_inn.in_(inns_)).all()
        classes = [ScraperSystem.get_from_path(scr.scraper_path)[0] for scr in scrs]
        return classes

    def create(self):
        """ Creates and adds the scraper path to the db """
        scr = self.get()
        if scr:
            return False
        user = UserDB(self.user_id).get()
        path = ScraperSystem(user.company_inn, self.cp_inn).create()
        if path:
            scraper = Scrapers(company_inn=self.cp_inn, scraper_path=path)
            db.session.add(scraper)
            db.session.commit()
            return True
        return False

    def delete(self):
        """ Deletes the scraper path from the db. Used when the file has already been deleted """
        scr = self.get()
        if not scr:
            return False
        db.session.delete(scr)
        db.session.commit()


class ItemUserDB:
    def __init__(self, user_id, url):
        self.user_id = user_id
        self.url = url

    def get(self) -> Union[UsersItems, None]:
        """ Gets the item by the link from the db """
        item = UsersItems.query.filter_by(user_id=self.user_id, link=self.url).first()
        if item:
            return item
        return None

    @staticmethod
    def get_all(user_id):
        """ Gets all the user items from the db """
        items = UsersItems.query.filter_by(user_id=user_id).all()
        return items

    def get_records(self) -> Union[list, None]:
        item_records = ItemsRecords.query.filter_by(link=self.url).all()
        if item_records:
            item_records = sorted(item_records, key=(lambda x: (x.date[-4:], x.date[-7:-5], x.date[:-8])), reverse=True)
            return item_records
        return None

    def get_web_info(self):
        """ Gets the info about the item from the internet via the link"""
        cp_inn = self.get_cp_inn()
        item_record = async_search.run_search_link(self.user_id, cp_inn, self.url)
        if not item_record:
            logging.warning(f"THERE IS NO ITEM IN {self.url}")
            return None
        return item_record

    def get_cp(self) -> Union[Companies, None]:
        """ Gets the competitor the items belong to """
        inn = self.get_cp_inn()
        if inn:
            return CompanyDB(inn).get()
        return None

    def get_cp_inn(self) -> Union[str, None]:
        """ Gets competitor's inn from a given link from the competitors table"""
        cps = CompetitorDB.get_all(self.user_id, connection_status="connected")
        for cp in cps:
            if cp.competitor_website in self.url:
                return cp.competitor_inn
        return None

    def get_format(self):
        """ Filter the info that gets to the server from the db about the item """
        item = self.get()
        item_refined = dict()
        if not item:
            return item_refined
        item_records = self.get_records()
        last_check = item_records[0]
        prev_check = item_records[1] if len(item_records) > 1 else last_check
        competitor_name = self.get_cp().organization

        item_refined["item_id"] = item.connection_id
        item_refined["name"] = last_check.item_name
        item_refined["competitor_inn"] = last_check.company_inn
        item_refined["competitor"] = competitor_name
        item_refined["last_price"] = last_check.price
        item_refined["last_date"] = last_check.date
        item_refined["price_change"] = last_check.price - prev_check.price
        item_refined["prev_price"] = prev_check.price
        item_refined["prev_date"] = prev_check.date
        item_refined["link"] = item.link

        return item_refined

    @staticmethod
    def get_format_all(user_id) -> list | None:
        items = ItemUserDB.get_all(user_id)
        if items:
            items_formatted = []
            for item in items:
                item_formatted = ItemUserDB(user_id, item.url).get_format()
                items_formatted.append(item_formatted)
            return items_formatted
        return None

    def record(self, item_name:str, item_price:str) -> bool:
        """ Records the info about the item to the db  """
        cp_inn = self.get_cp_inn()

        item = ItemsRecords(item_name=item_name,
                            company_inn=cp_inn,
                            price=item_price,
                            date=DateCur.cur_date(),
                            link=self.url)
        db.session.add(item)

        connection_exists = self.get()
        if not connection_exists:
            connection = UsersItems(user_id=self.user_id, link=self.url)
            db.session.add(connection)
        db.session.commit()
        return True

    def update(self) -> bool:
        """ Updates the info about the item only when it's been ITEMS_UPDATE days since the last update"""
        item_records = self.get_records()
        if not item_records:
            item_records_web = self.get_web_info()
            if not item_records_web:
                return False
            return self.record(item_records["name"], item_records["price"])  # True or False depending on if the recording went well

        last_record = item_records[0].date
        days_passed = DateCur.days_passed(last_record.date)
        if days_passed < ITEMS_UPDATE:
            logging.warning(f"ITEM {last_record.item_name} HAS ALREADY BEEN CHECKED {last_record.date}")
            return False

        item_records_web = self.get_web_info()
        if not item_records_web:
            return False
        return self.record(item_records_web["name"], item_records_web["price"])


def db_add_item_mnl(user_id, company_inn, item_name, price, link):
    date = get_cur_date()
    # date randomizer
    # date = get_cur_date().replace("13", str(random.choice(list(range(10, 30)))))
    item_records = db_get_item_records(link)
    if item_records:
        last_date = item_records[0].date
        if date == last_date:
            print(last_date, "already checked today")
        else:
            item = {"name": item_name, "price": price, "url": link}
            print("Not checked today. Last time is", last_date)
            item = ItemsRecords(item_name=item["name"],
                                company_inn=company_inn,
                                price=item["price"],
                                date=date,
                                link=link)
            db.session.add(item)
    else:
        item = {"name": item_name, "price": price, "url": link}
        print("Has never been added. Adding...")
        item = ItemsRecords(item_name=item["name"],
                            company_inn=company_inn,
                            price=item["price"],
                            date=date,
                            link=link)
        db.session.add(item)
    connection_exists = UsersItems.query.filter_by(user_id=user_id, link=link).first()
    if not connection_exists:
        connection = UsersItems(user_id=user_id, link=link)
        db.session.add(connection)
    db.session.commit()
    return True


def db_add_refreshed_item(item_name, company_inn, price, link, date):
    item_records = db_get_item_records(link)
    if item_records:
        last_date = item_records[0].date
        if date == last_date:
            print(last_date, "already checked today")
            return
    if not price:
        price = 0
    item = ItemsRecords(item_name=item_name,
                        company_inn=company_inn,
                        price=price,
                        date=date,
                        link=link)
    db.session.add(item)
    db.session.commit()


def db_refresh_all_items(user_id):
    items_connections = UsersItems.query.filter_by(user_id=user_id).all()
    pass


def db_delete_item_connection(user_id, connection_id):
    item_connection = UsersItems.query.filter_by(user_id=user_id, connection_id=connection_id)
    if item_connection.first():
        date = get_cur_date()
        link = item_connection.first().link
        print(link)
        item_last_record = ItemsRecords.query.filter_by(date=date, link=item_connection.first().link)
        item_last_record.delete()
        item_connection.delete()
        db.session.commit()
        return True
    return False


def db_get_item_link_new(user_id, company_inn, item_name):
    # the soul purpose of the funk is to get the number to a manually added item and
    # recognize if the item has ever been added
    item_link = get_link(db_get_user_website(user_id, company_inn))
    item_name = item_name.strip()
    exist = ItemsRecords.query.filter_by(item_name=item_name, company_inn=company_inn).first()
    if exist:
        return exist.link
    item_id = db.session.query(func.max(ItemsRecords.item_id)).scalar()
    item_link = item_link + f"/{1000 + item_id + 1}"
    return item_link


def db_get_item_connection(user_id, user_link, comp_inn):
    linked_items = ItemsConnections.query.filter_by(user_id=user_id, item_link=user_link).all()
    for item in linked_items:
        if str(db_get_inn(user_id, item.connected_item_link)) == str(comp_inn):
            return item
    return None


def db_add_item_connection(user_id, item_link, connected_item_link, comp_inn):
    exists = ItemsConnections.query.filter_by(user_id=user_id, item_link=item_link,
                                              connected_item_link=connected_item_link).first()
    if exists:
        return False
    exists = db_get_item_connection(user_id=user_id, user_link=item_link, comp_inn=comp_inn)
    if exists:
        print('ex.............................')
        exists.connection_item_link = connected_item_link
        db.session.commit()
        return True
    new_connection = ItemsConnections(user_id=user_id, item_link=item_link, connected_item_link=connected_item_link)
    db.session.add(new_connection)
    db.session.commit()
    return True


def db_get_item_link(user_id, item_id):
    item = UsersItems.query.filter_by(user_id=user_id, connection_id=item_id).first()
    if item:
        return item.link
    return None


def db_delete_connection(user_id, item_link, linked_item_link):
    exists = ItemsConnections.query.filter_by(user_id=user_id, item_link=item_link,
                                              connected_item_link=linked_item_link)
    if exists.first():
        exists.delete()
        db.session.commit()


class UserDB:
    def __init__(self, user_id):
        self.user_id = user_id

    def get(self):
        user = User.query.filter_by(id=self.user_id).first()
        if user:
            return user
        return None

    def db_change_website(user_id, inn, new_website):
        # the changed info about the user is stored in the competitors table where the user his own
        # competitor. If the user wants to change his email for the first time, we add him to the table.

        requested = Competitors.query.filter_by(user_id=user_id, competitor_inn=inn).first()
        new_web = get_link(new_website)
        if requested and new_web:
            print("in1")
            requested.competitor_website = new_web
            db.session.commit()
            return True
        elif new_web:
            print("in2")
            db_add_competitor(user_id, inn, website=new_web)
            return True
        else:
            logging.warning(f"The website for {inn} hasn't been changed")
            return False

        def db_get_user_website(user_id, inn):
            """When the user hasn't requested connection yet, he sees companies website from
            the companies table as a default. Returns the object from the db that will show the needed website"""
            requested = Competitors.query.filter_by(user_id=user_id, competitor_inn=inn).first()
            if requested:
                return requested.competitor_website
            return Companies.query.filter_by(_inn=inn).first().website

        def db_get_users_connections(user_id):
            return ItemsConnections.query.filter_by(user_id=user_id).all()
