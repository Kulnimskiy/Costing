from . import db
from .models import Companies, User, Competitors
from .web_scrapers.company_info_search import Company
from datetime import datetime
from .helpers import get_cur_date


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


def db_get_competitors(user_id):
    return Competitors.query.filter_by(user_id=user_id)


def db_delete_competitor(user_id, com_inn):
    company = Competitors.query.filter_by(user_id=user_id, competitor_inn=com_inn).first()
    if company:
        print(company)
        db.session.delete(company)
        db.session.commit()
    return


def get_all_competitors():
    users = Competitors.query.all()
    for user in users:
        print(user.__dict__)
