from . import db
from .models import Companies, User
from .web_scrapers.company_info_search import Company
from datetime import datetime
from .helpers import get_cur_date


def load_company_data(_inn):
    """Uses a parser to get data from the web if the last load of the date
    happened more than 2 days ago and updates the data in the db"""
    days_between_reload = 1
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
            return company.__dict__
        print("GET", company.__dict__)
        return company.__dict__

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
    return company_info
