from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)  # primary keys are required by the lib
    company_name = db.Column(db.String(100), nullable=False)
    company_inn = db.Column(db.Integer(), unique=True, nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # UserMixin looks for and id column using get_id(). We got _id attr instead
    def get_id(self):
        return self._id


class Companies(db.Model):
    _inn = db.Column("inn", db.Integer, primary_key=True)
    website = db.Column(db.String(200))
    organization = db.Column(db.String(200))
    ogrn = db.Column(db.Integer())
    registration_date = db.Column(db.String(100))
    sphere = db.Column(db.String(400))
    address = db.Column(db.String(400))
    workers_number = db.Column(db.Integer())
    ceo = db.Column(db.String(100))
    info_loading_date = db.Column(db.String(100))


class Competitors(db.Model):
    connection_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    competitor_inn = db.Column(db.Integer, nullable=False)
    competitor_nickname = db.Column(db.String(100))
    competitor_website = db.Column(db.String(200))
    # connection statuses are disconnected, connected, requested
    connection_status = db.Column(db.String(200), default="disconnected", nullable=False)


class Scrapers(db.Model):
    scraper_id = db.Column(db.Integer, primary_key=True)
    company_inn = db.Column(db.Integer, nullable=False)
    scraper_path = db.Column(db.String(200), nullable=False)
