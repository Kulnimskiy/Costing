import logging
from sqlalchemy import func
from sqlalchemy.sql import text
from project import db
from project.models import Companies, Competitors, Scrapers, ItemsRecords, UsersItems, ItemsConnections, User
from project.search_files.search_company import Company
from project.systems import ScraperSystem
from project.managers import UrlManager
from project.helpers import DateCur
from project.search_files import async_search

DAYS_BEFORE_RELOAD = 3  # Number of days to update the info about a company
ITEMS_UPDATE = 1  # Number of days to add new records of the item


class CompanyDB:
    model = Companies

    def __init__(self, inn):
        self.inn = inn

    def get(self) -> Companies | None:
        """ Get the company info from the db """
        company = self.model.query.filter_by(inn=self.inn).first()
        if company:
            return company
        return None

    def get_web(self):
        company = self.get()
        if company:
            return company.website
        return None

    def change_web(self, new_web):
        company = self.get()
        if not company:
            return False
        new_web = UrlManager(new_web).check()
        if not new_web:
            logging.warning(f"COMPANY '{self.get().organization}' WEBSITE HASN'T BEEN CHANGED")
            return False
        company.website = new_web
        db.session.commit()
        return True

    @staticmethod
    def create_from_user(user_inn):
        company = CompanyDB(user_inn).get()
        if company:
            logging.warning(f"THE COMPANY {user_inn} WAS ALREADY CREATED")
            return False
        user: User = UserDB.get_from_inn(user_inn)
        if not user:
            logging.warning(f"COMPANY WASN'T CREATED FROM THE USER {user_inn}")
            return False
        new_company = Companies(inn=user.company_inn,
                                website=None,
                                organization=user.company_name,
                                ogrn=None,
                                registration_date=None,
                                sphere=None,
                                address=None,
                                workers_number=None,
                                ceo=None,
                                info_loading_date=DateCur.cur_datetime())
        db.session.add(new_company)
        db.session.commit()
        logging.warning(f"THE COMPANY HAS BEEN CREATED {user_inn} FROM THE USER")
        return True

    def create(self) -> bool:
        """ Creates a company from its inn and adds it to the db """

        if self.get():  # Check if the company already exists
            return False

        company_info = Company(self.inn).get_full_info()
        if company_info is None:
            logging.warning(f"THE COMPANY {self.inn} WASN'T CREATED")
            return False

        new_company = Companies(inn=company_info["inn"],
                                website=company_info["website"],
                                organization=company_info["organization"],
                                ogrn=company_info["ogrn"],
                                registration_date=company_info["registration_date"],
                                sphere=company_info["sphere"],
                                address=company_info["address"],
                                workers_number=company_info["workers_number"],
                                ceo=company_info["ceo"],
                                info_loading_date=DateCur.cur_datetime())
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
        company.info_loading_date = DateCur.cur_datetime()

        # if there is new info about a website, we change it
        web = company_info["website"]
        if web and company.website != UrlManager(web).check():
            company.website = UrlManager(web).check()
        db.session.commit()
        return True

    def load(self) -> Companies | None:
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

    def __init__(self, user_id: int, cp_inn: str):
        self.user_id = user_id
        self.cp_inn = cp_inn

    def get(self) -> Competitors | None:
        competitor = Competitors.query.filter_by(user_id=self.user_id, competitor_inn=self.cp_inn).first()
        if not competitor:
            return None
        return competitor

    def get_web(self) -> str | None:
        cp = self.get()
        if not cp:
            return None
        return cp.competitor_website

    def change_web(self, new_web: str) -> bool:
        cp = self.get()
        if not cp:
            return False
        new_web = UrlManager(new_web).check()
        if not new_web:
            logging.warning(f"COMPATITOR '{self.get().organization}' WEBSITE HASN'T BEEN CHANGED")
            return False
        cp.competitor_website = new_web
        db.session.commit()
        return True

    @staticmethod
    def get_all(user_id, connection_status="") -> list[Competitors]:
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
        ScraperDB(user_id=self.user_id, cp_inn=self.cp_inn).create()
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
        user = UserDB(self.user_id).get()
        if not user:
            return False
        if not cp:
            logging.warning(f"THE COMPANY {self.cp_inn} IS NOT A COMPETITOR FOR USER: {self.user_id}")
            return False

        # save the scraper path to know if it's used anywhere
        scraper = ScraperDB(self.user_id, self.cp_inn)
        scr_path = scraper.get_path()
        db.session.delete(cp)
        db.session.commit()

        scr_times_used = len(Competitors.query.filter_by(competitor_inn=self.cp_inn).all())
        if scr_times_used == 0:
            if ScraperSystem(user.company_inn, self.cp_inn).delete(scr_path):
                logging.warning(f"SCRAPER PATH {self.cp_inn} WILL BE DELETED")
                scraper.delete()  # deletes the path only when the scraper is deleted
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
            logging.warning(f"THE SCRAPER FOR {scr.company_inn} ALREADY EXISTS")
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


class ItemDB:
    def __init__(self, user_id: int, url: str):
        self.user_id = user_id
        self.url = url

    def get(self) -> UsersItems | None:
        """ Gets the item by the link from the db """
        item = UsersItems.query.filter_by(user_id=self.user_id, link=self.url).first()
        if item:
            return item
        return None

    @staticmethod
    def get_by_id(user_id, item_id) -> UsersItems | None:
        item = UsersItems.query.filter_by(user_id=user_id, connection_id=item_id).first()
        if item:
            return item
        return None

    @staticmethod
    def get_all(user_id) -> list[UsersItems]:
        """ Gets all the user items from the db """
        items = UsersItems.query.filter_by(user_id=user_id).all()
        return items

    def get_record(self):
        """ Gets the last record about an item """
        item_record = ItemsRecords.query.filter_by(link=self.url).order_by(text("date desc")).first()
        if item_record:
            return item_record
        return None

    def get_records(self) -> list | None:
        """ Gets all records about an item """
        item_records = ItemsRecords.query.filter_by(link=self.url).order_by(text("date desc")).all()
        if item_records:
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

    def get_cp(self) -> Companies | None:
        """ Gets the competitor the items belong to """
        inn = self.get_cp_inn()
        if inn:
            return CompanyDB(inn).get()
        return None

    def get_cp_inn(self, scope="") -> str | None:
        """ Gets competitor's inn from a given link from the competitors table
        :param scope - limits the list of competitors to only 'connected' ones, 'requested' or 'disconnected'"""
        scopes = ["connected", "requested", "disconnected", ""]
        if scope not in scopes:
            return None
        cps = CompetitorDB.get_all(self.user_id, connection_status=scope)
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
        if not item_records:
            ItemDB(user_id=self.user_id, url=self.url).update()
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
    def get_format_all(user_id) -> list[dict] | None:
        items = ItemDB.get_all(user_id)
        if items:
            items_formatted = []
            for item in items:
                item_formatted = ItemDB(user_id, item.link).get_format()
                items_formatted.append(item_formatted)
            return items_formatted
        return None

    def create(self, item_name: str, item_price: int | float) -> bool:
        """ Records the info about the item to the db if the permission is given """
        if not self.__permission():
            return False

        """You can create items only from connected competitors"""
        cp_inn = self.get_cp_inn(scope="connected")
        if not cp_inn:
            return False

        if not item_price:  # if there is no price for the item, set it to 0
            item_price = 0

        item = ItemsRecords(item_name=item_name,
                            company_inn=cp_inn,
                            price=item_price,
                            date=DateCur.cur_datetime(),
                            link=self.url)
        db.session.add(item)

        connection_exists = self.get()
        if not connection_exists:
            connection = UsersItems(user_id=self.user_id, link=self.url)
            db.session.add(connection)
        db.session.commit()
        return True

    def update(self) -> bool:
        """ Updates the info about from the web """
        if not self.__permission():
            return False

        item_records_web = self.get_web_info()
        if not item_records_web:
            return False
        return self.create(item_records_web["name"],
                           item_records_web["price"])  # True or False depending on if the recording went well

    def __permission(self) -> bool:
        """ Gives permission to create new records about an item if It's been >= ITEMS_UPDATE days"""
        last_record = self.get_record()
        if not last_record:
            logging.warning(f"ITEM {self.url} HAS NEVER BEEN ADDED. ADDING...")
            return True
        days_passed = DateCur.days_passed(last_record.date)
        print(days_passed)
        if days_passed < ITEMS_UPDATE:

            logging.warning(f"ITEM {last_record.item_name} HAS ALREADY BEEN CHECKED {last_record.date}")
            return False
        return True

    def delete(self):
        item = self.get()
        if not item:
            return False
        last_record = self.get_record()
        if not last_record:
            return False
        db.session.delete(last_record)
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def generate_url(user_id, company_inn, item_name) -> str:
        """ Generate a unique web url to identify a manually added item in the db
            if it hasn't been given or not valid """
        user = UserDB(user_id)
        if not user:
            raise ValueError("The user doesn't exist")
        item_link = UrlManager(user.get_web()).check()
        item_name = item_name.strip()

        exist = ItemsRecords.query.filter_by(item_name=item_name, company_inn=company_inn).first()
        if exist:
            logging.warning(f"THE ITEM '{item_name}' IS ALREADY IN THE DB! RETURNING ITS URL!")
            return exist.link

        item_id = db.session.query(func.max(ItemsRecords.item_id)).scalar()
        item_link = item_link + f"/{1000 + item_id + 1}"
        logging.warning(f"ITEM '{item_name}' HAS BEEN GIVEN THE URL {item_link}!")
        return item_link


class RelationsDB:
    """ Manages items relationships in the db """

    def __init__(self, user_id: int, item_url: str):
        self.user_id = user_id
        self.item_url = item_url

    @staticmethod
    def get_all(user_id) -> list | None:
        items_related = ItemsConnections.query.filter_by(user_id=user_id).all()
        if items_related:
            return items_related
        return None

    def get_by_inn(self, cp_inn: str) -> ItemsConnections | None:
        """ Gets the related item for the item_link from a specific competitor"""
        items_related = self.get_relations()
        if not items_related:
            return None
        for item in items_related:
            if ItemDB(self.user_id, item.connected_item_link).get_cp_inn() == cp_inn:
                return item
        return None

    def get_by_url(self, related_item_url) -> ItemsConnections | None:
        item_related = ItemsConnections.query.filter_by(user_id=self.user_id,
                                                        item_link=self.item_url,
                                                        connected_item_link=related_item_url).first()
        if item_related:
            return item_related
        return None

    def get_relations(self) -> list | None:
        items_related = ItemsConnections.query.filter_by(user_id=self.user_id, item_link=self.item_url).all()
        if items_related:
            return items_related
        return None

    def create_relation(self, cp_inn: str, related_item_url: str) -> bool:
        rel_exists = ItemsConnections.query.filter_by(user_id=self.user_id,
                                                      item_link=self.item_url,
                                                      connected_item_link=related_item_url).first()
        if rel_exists:  # return if the relation like this has already been established
            return False

        # check if there is a related item for the item_link from a specific competitor
        cp_rel_exists = self.get_by_inn(cp_inn)
        if cp_rel_exists:
            cp_rel_exists.connection_item_link = related_item_url
            db.session.commit()
            logging.warning("REPLACING OLD CONNECTED LINK WITH A NEW ONE")
            return True
        new_connection = ItemsConnections(user_id=self.user_id,
                                          item_link=self.item_url,
                                          connected_item_link=related_item_url)
        db.session.add(new_connection)
        db.session.commit()
        return True

    def update_relation(self, cp_inn, related_item_url):
        cp_rel_exists = self.get_by_inn(cp_inn)
        if not cp_rel_exists:
            return False
        cp_rel_exists.connection_item_link = related_item_url
        db.session.commit()
        return True

    def delete_relation(self, related_item_url: str) -> bool:
        exists = self.get_by_url(related_item_url)
        if exists:
            db.session.delete(exists)
            db.session.commit()
            return True
        return False

    def delete_all_relations(self) -> bool:
        relates_to = ItemsConnections.query.filter_by(user_id=self.user_id,
                                                      item_link=self.item_url).all()
        related_to = ItemsConnections.query.filter_by(user_id=self.user_id,
                                                      connected_item_link=self.item_url).all()
        relates_to.extend(related_to)
        for relation in relates_to:
            db.session.delete(relation)
        db.session.commit()
        return True

    def get_format(self):
        """ Formats 1 item the right way for the profile page"""

    @staticmethod
    def get_format_all(user_id, user_inn) -> dict[tuple, dict[int, dict]] | None:
        """ Formatted for the front end data about user's item connections
            The format is:
            {(item["item_id"], item["name"], item['link']):
            {"comp_inn_1": {"url": connected_item_link, "name": item_name"}, ...},
             ...}
        """

        all_items = ItemDB.get_format_all(user_id)
        if not all_items:
            return None
        own_items = list(filter(lambda x: x["competitor_inn"] == str(user_inn), all_items))
        all_linked_items = RelationsDB.get_all(user_id)
        all_linked_items = all_linked_items if all_linked_items else []  # None type obj is not iterable

        formatted_relations = dict()
        # if not all_linked_items:
        #     return formatted_relations

        for item in own_items:
            related = dict()
            for linked_item in all_linked_items:
                if item['link'] == linked_item.item_link:
                    con_item = ItemDB(user_id, linked_item.connected_item_link).get_format()
                    comp_inn = con_item["competitor_inn"]
                    related[comp_inn] = {"url": linked_item.connected_item_link, "name": con_item["name"]}
            formatted_relations[(item["item_id"], item["name"], item['link'])] = related
        return formatted_relations

    @staticmethod
    def get_format_compare(user_id, user_inn):
        user_inn = UserDB(user_id).get().company_inn
        all_items = ItemDB.get_format_all(user_id)
        own_items = list(filter(lambda x: x["competitor_inn"] == str(user_inn), all_items))
        all_linked_items = RelationsDB.get_all(user_id)
        all_linked_items = all_linked_items if all_linked_items else []
        items_info = dict()
        for item in own_items:
            item_url = item['link']
            info = {"name": item['name'],
                    "url": item['link'],
                    "my_price": item['last_price'],
                    "max_price": 0,
                    "min_price": 0,
                    "avg_price": 0.0,
                    "cr_prices": dict()}
            for linked_item in all_linked_items:
                if linked_item.item_link == item_url:
                    cr_item = ItemDB(user_id, linked_item.connected_item_link).get_format()
                    cr_inn = cr_item["competitor_inn"]
                    info["cr_prices"][cr_inn] = cr_item
            cr_prices = [item["last_price"] for item in info["cr_prices"].values() if item["last_price"] > 0]
            if cr_prices:
                info["max_price"] = max(cr_prices)
                info["min_price"] = min(cr_prices)
                print("sum", sum(cr_prices), "len ", len(cr_prices))
                info["avg_price"] = round(sum(cr_prices) / len(cr_prices), 1)
            items_info[f"{item_url}"] = info
        return items_info


class UserDB:
    def __init__(self, user_id):
        self.user_id = user_id

    def get(self) -> User | None:
        user = User.query.filter_by(id=self.user_id).first()
        if user:
            return user
        return None

    @staticmethod
    def get_from_inn(inn):
        user = User.query.filter_by(company_inn=inn).first()
        if not user:
            return None
        return user

    def change_email(self, new_email):
        """ Changes user's email to a new one"""
        user = self.get()
        if not user:
            return False
        user.email = new_email
        db.session.commit()
        return True

    def get_web(self):
        """When the user hasn't requested connection yet, he sees companies website from
        the companies table as a default. Returns the object from the db that will show the needed website"""
        user = self.get()
        if not user:
            return False
        user_inn = user.company_inn
        requested = CompetitorDB(self.user_id, user_inn).get()
        if requested:
            return requested.competitor_website
        return CompanyDB(user_inn).get().website

    def change_web(self, new_website):
        """ The changed info about the user is stored in the competitors table where the user his own
            competitor. If the user wants to change his website for the first time, we add him to the table."""
        user = self.get()
        if not user:
            return False
        user_inn = user.company_inn

        new_web = UrlManager(new_website).check()
        if not new_web:
            return False

        # the user company gets into the Competitors table only when the connection request has been sent
        competitor = CompetitorDB(self.user_id, user_inn)
        company = CompanyDB(user_inn)

        if competitor.get():
            competitor.change_web(new_web)
            return True
        elif company.get():
            company.change_web(new_web)
            return True
        else:
            logging.warning(f"The website for {user_inn} hasn't been changed")
            return False
