import logging
import random
from sqlalchemy import func
from datetime import datetime
from project import db
from project.models import Companies, Competitors, Scrapers, ItemsRecords, UsersItems, ItemsConnections
from project.corpotate_scrapers.company_info_search import Company
from project.file_manager import create_scraper_file
from project.helpers import get_cls_from_path, get_cur_date, get_link
from project import async_search


def load_company_data(_inn):
    """Uses a parser to get data from the web if the last load of the date
    happened more than 2 days ago and updates the data in the db"""
    days_between_reload = 3
    cur_date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur_date = datetime.strptime(cur_date_str, "%Y-%m-%d %H:%M:%S")
    company = Companies.query.filter_by(_inn=_inn).first()
    if company:
        last_load_date = datetime.strptime(company.info_loading_date, "%Y-%m-%d %H:%M:%S")
        days_passed = (cur_date - last_load_date).days
        if days_passed >= days_between_reload:
            # update the company info
            company_info = Company(_inn).get_full_info()
            company.inn = company_info["inn"]

            # if there is new info about a website, we change it
            if company_info["website"]:
                company.website = company_info["website"]
            company.organization = company_info["organization"]
            company.ogrn = company_info["ogrn"]
            company.registration_date = company_info["registration_date"]
            company.sphere = company_info["sphere"]
            company.address = company_info["address"]
            company.workers_number = company_info["workers_number"]
            company.ceo = company_info["ceo"]
            company.info_loading_date = str(cur_date)
            db.session.commit()

            # need to get that again after the commit
            company = Companies.query.filter_by(_inn=_inn).first()
            # print("CHANGE", company.__dict__)
            return company
        # print("GET", company.__dict__)
        return company

    # if the company hasn't been added yet, we add it
    company_info = Company(_inn).get_full_info()
    new_company = Companies(_inn=company_info["inn"],
                            website=company_info["website"],
                            organization=company_info["organization"],
                            ogrn=company_info["ogrn"],
                            registration_date=company_info["registration_date"],
                            sphere=company_info["sphere"],
                            address=company_info["address"],
                            workers_number=company_info["workers_number"],
                            ceo=company_info["ceo"],
                            info_loading_date=cur_date_str)
    db.session.add(new_company)

    # also we add it to the list of competitors so that it could be connected
    # db_add_competitor()
    db.session.commit()
    company = Companies.query.filter_by(_inn=_inn).first()
    return company


def create_competitor(data_source, user_id, comp_inn, comp_nickname=None, website=None):
    comp_nickname = comp_nickname if comp_nickname else data_source.organization
    website = website if website else data_source.website
    if website:
        if "http" not in website and "https" not in website:
            website = "https://" + website
    new_competitor = Competitors(user_id=user_id,
                                 competitor_inn=comp_inn,
                                 competitor_nickname=comp_nickname,
                                 competitor_website=website)
    return new_competitor


def db_add_competitor(user_id, comp_inn, comp_nickname=None, website=None):
    competitor_already_added = Competitors.query.filter_by(competitor_inn=comp_inn, user_id=user_id).first()
    if competitor_already_added:
        print(competitor_already_added.__dict__)
        print("Competitor is already in the table")
        return competitor_already_added

    company_exists = Companies.query.filter_by(_inn=comp_inn).first()
    if company_exists:
        print("The company exists already in the table")
        new_competitor = create_competitor(company_exists, user_id, comp_inn, comp_nickname, website)
        db.session.add(new_competitor)
        db.session.commit()
        return 0
    print("adding a company")
    # if there is no company no competitor with this inn and
    company = load_company_data(comp_inn)
    new_competitor = create_competitor(company, user_id, comp_inn, comp_nickname, website)
    db.session.add(new_competitor)
    db.session.commit()


def db_get_competitors(user_id, connection_status=""):
    """connection status can be 'disconnected', 'connected','requested'. Only those are in the db"""
    if connection_status:
        return Competitors.query.filter_by(user_id=user_id, connection_status=connection_status).all()
    return Competitors.query.filter_by(user_id=user_id).all()


def db_get_competitor(user_id, com_inn):
    return Competitors.query.filter_by(user_id=user_id, competitor_inn=com_inn).first()


def db_update_con_status(user_id, com_inn, new_status="requested"):
    competitor = db_get_competitor(user_id, com_inn)
    if competitor and competitor.connection_status == "disconnected":
        competitor.connection_status = new_status
        db.session.commit()
        return True
    return False


def db_delete_competitor(user_id, com_inn):
    company = db_get_competitor(user_id, com_inn)
    if company:
        db.session.delete(company)
        db.session.commit()
        return True
    return False


def get_all_competitors():
    users = Competitors.query.all()
    for user in users:
        print(user.__dict__)


def db_add_scraper(user_inn, comp_inn: str):
    exists = Scrapers.query.filter_by(company_inn=comp_inn).first()
    if exists:
        return False
    path = create_scraper_file(user_inn, comp_inn)
    if path:
        scraper = Scrapers(company_inn=comp_inn, scraper_path=path)
        db.session.add(scraper)
        db.session.commit()
        return True
    return False


def db_get_scr_from_id(user_id, comp_inn=None, path=False):
    """ If competitor's inn is not provided, it returns a list of all the scrapers connected
    to the user by their id. Else it returns a scraper for a specific competitor"""
    if comp_inn:
        competitor = db_get_competitor(user_id, comp_inn)
        if competitor:
            scr_path = Scrapers.query.filter_by(company_inn=comp_inn).first().scraper_path
            if path:
                return scr_path
            if competitor.connection_status == "connected":
                cls = get_cls_from_path(scr_path)[0]
                return cls
            else:
                print(f"The competitor {comp_inn} is not connected")
                return None
    competitors_ = db_get_competitors(user_id, "connected")
    inns_ = [competitor.competitor_inn for competitor in competitors_]
    scr_path = Scrapers.query.filter(Scrapers.company_inn.in_(inns_)).all()
    classes = [get_cls_from_path(scr.scraper_path)[0] for scr in scr_path]
    return classes


def db_delete_scr_path(user_id, comp_inn):
    scraper = Scrapers.query.filter_by(company_inn=comp_inn).first()
    if scraper:
        db.session.delete(scraper)
        db.session.commit()


def db_add_item(user_id, company_inn, link):
    date = get_cur_date()
    # date randomizer
    # date = get_cur_date().replace("13", str(random.choice(list(range(10, 30)))))
    item_records = db_get_item_records(link)
    if item_records:
        last_date = item_records[0].date
        if date == last_date:
            print(last_date, "already checked today")
        else:
            item = async_search.run_search_link(user_id, company_inn, link)
            if not item:
                print("there is no such item")
                return False
            print("Not checked today. Last time is", last_date)
            item = ItemsRecords(item_name=item["name"],
                                company_inn=company_inn,
                                price=item["price"],
                                date=date,
                                link=link)
            db.session.add(item)
    else:
        item = async_search.run_search_link(user_id, company_inn, link)
        if not item:
            print("there is no such item")
            return False
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
    item = ItemsRecords(item_name=item_name,
                        company_inn=company_inn,
                        price=price,
                        date=date,
                        link=link)
    db.session.add(item)
    db.session.commit()


def db_get_items(user_id):
    items_connections = UsersItems.query.filter_by(user_id=user_id).all()
    if items_connections:
        items_refined = []
        for item in items_connections:
            item_refined = dict()
            item_records = db_get_item_records(item.link)
            last_check = item_records[0]
            if len(item_records) > 1:
                prev_check = item_records[1]
            else:
                prev_check = last_check
            item_refined["item_id"] = item.connection_id
            item_refined["name"] = last_check.item_name
            item_refined["competitor_inn"] = int(last_check.company_inn)
            item_refined["competitor"] = Companies.query.filter_by(_inn=last_check.company_inn).first().organization
            item_refined["last_price"] = last_check.price
            item_refined["last_date"] = last_check.date
            item_refined["price_change"] = last_check.price - prev_check.price
            item_refined["prev_price"] = prev_check.price
            item_refined["prev_date"] = prev_check.date
            item_refined["link"] = item.link
            items_refined.append(item_refined)
        return items_refined
    return []


def db_get_item(user_id, item_link):
    item = UsersItems.query.filter_by(user_id=user_id, link=item_link).first()
    item_refined = dict()
    if not item:
        return item_refined
    item_records = db_get_item_records(item_link)
    last_check = item_records[0]
    if len(item_records) > 1:
        prev_check = item_records[1]
    else:
        prev_check = last_check
    item_refined["item_id"] = item.connection_id
    item_refined["name"] = last_check.item_name
    item_refined["competitor_inn"] = int(last_check.company_inn)
    item_refined["competitor"] = Companies.query.filter_by(_inn=last_check.company_inn).first().organization
    item_refined["last_price"] = last_check.price
    item_refined["last_date"] = last_check.date
    item_refined["price_change"] = last_check.price - prev_check.price
    item_refined["prev_price"] = prev_check.price
    item_refined["prev_date"] = prev_check.date
    item_refined["link"] = item.link
    return item_refined


def db_get_item_records(link):
    item_records = ItemsRecords.query.filter_by(link=link).all()
    if item_records:
        item_records = sorted(item_records, key=(lambda x: (x.date[-4:], x.date[-7:-5], x.date[:-8])), reverse=True)
        return item_records
    return None


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


def db_get_user_website(user_id, inn):
    """When the user hasn't requested connection yet, he sees companies website from
    the companies table as a default. Returns the object from the db that will show the needed website"""
    requested = Competitors.query.filter_by(user_id=user_id, competitor_inn=inn).first()
    if requested:
        return requested.competitor_website
    return Companies.query.filter_by(_inn=inn).first().website


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
        if str(db_get_inn(item.connected_item_link)) == str(comp_inn):
            return item
    return None


def db_get_users_connections(user_id):
    return ItemsConnections.query.filter_by(user_id=user_id).all()


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


def db_get_inn(link: str):
    """gets competitor's inn from a given link from the ItemsRecords table"""
    item = ItemsRecords.query.filter_by(link=link).first()
    if not item:
        return None
    return item.company_inn


def db_delete_connection(user_id, item_link, linked_item_link):
    exists = ItemsConnections.query.filter_by(user_id=user_id, item_link=item_link,
                                              connected_item_link=linked_item_link)
    if exists.first():
        exists.delete()
        db.session.commit()
