import random
from datetime import datetime
from project import db
from project.models import Companies, Competitors, Scrapers, ItemsRecords, UsersItems
from project.corpotate_scrapers.company_info_search import Company
from project.file_manager import create_scraper_file
from project.helpers import get_cls_from_path, get_cur_date


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
            print("CHANGE", company.__dict__)
            return company
        print("GET", company.__dict__)
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
        print(company)
        db.session.delete(company)
        db.session.commit()
    return


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


def db_get_scr_from_id(user_id, comp_inn=None):
    """ If competitor's inn is not provided, it returns a list of all the scrapers connected
    to the user by their id. Else it returns a scraper for a specific competitor"""
    if comp_inn:
        competitor = db_get_competitor(user_id, comp_inn)
        if competitor:
            scr_path = Scrapers.query.filter_by(company_inn=comp_inn).first().scraper_path
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


def db_add_item(user_id, item_name, company_inn, price, link):
    date = get_cur_date()
    # date randomizer
    # date = get_cur_date().replace("13", str(random.choice(list(range(10, 30)))))

    item_records = db_get_item_records(link, company_inn)
    if item_records:
        last_date = item_records[0].date
        if date == last_date:
            print(last_date, "already checked today")
        else:
            item = ItemsRecords(item_name=item_name,
                                company_inn=company_inn,
                                price=price,
                                date=date,
                                link=link)
            db.session.add(item)
    connection_exists = UsersItems.query.filter_by(user_id=user_id, link=link).first()
    if not connection_exists:
        connection = UsersItems(user_id=user_id, link=link)
        db.session.add(connection)
    db.session.commit()
    return True


def db_get_items(user_id):
    items_connections = UsersItems.query.filter_by(user_id=user_id).all()
    items_connections = UsersItems.query.filter_by(user_id=user_id).all()
    items_links = [items_link.link for items_link in items_connections]
    print(items_links)
    items = ItemsRecords.query.filter(ItemsRecords.link.in_(items_links)).all()
    # for item in items:
    #     item.__dict__["name"] = "12"
    #     item.__dict__["name"] = "12"
    #     item.__dict__["name"] = "12"
    #     item.__dict__["name"] = "12"
    for item in items:
        print()
        print()
        print(item.__dict__)
    return items

    # item.name
    # item.competitor
    # item.last_price
    # item.last_date
    # item.price_change
    # item.prev_price
    # item.prev_date
    # item.link
    # item.last_price


def db_get_item_records(link, company_inn):
    item_records = ItemsRecords.query.filter_by(link=link, company_inn=company_inn).all()
    if item_records:
        item_records = sorted(item_records, key=(lambda x: (x.date[-4:], x.date[-7:-5], x.date[:-8])), reverse=True)
        # for i in items_records:
        #     print(i.date)
        last_date = item_records[0].date
        print(last_date, " :last date")
        return item_records
    return None
