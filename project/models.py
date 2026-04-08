from flask_login import UserMixin
from project import db


class User(UserMixin, db.Model):
    _id = db.Column(
        "id", db.Integer, primary_key=True
    )  # primary keys are required by the lib
    company_name = db.Column(db.String(100), nullable=False)
    company_inn = db.Column(db.Integer(), unique=True, nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # UserMixin looks for and id column using get_id(). We got _id attr instead
    def get_id(self):
        return self._id


class Companies(db.Model):
    _inn = db.Column("inn", db.String(20), primary_key=True)  # INN can be 10-12 digits
    website = db.Column(db.String(200), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    ogrn = db.Column(db.String(20))  # store as string, not integer
    registration_date = db.Column(db.Date, nullable=True)  # store as date object
    sphere = db.Column(db.String(400), nullable=True)
    address = db.Column(db.String(400), nullable=True)
    workers_number = db.Column(db.Integer(), default=0)
    ceo = db.Column(db.String(100), nullable=True)
    info_loading_date = db.Column(db.DateTime, nullable=True)


class Competitors(db.Model):
    """Stores the info about users' competitors and their connection statuses.
    The required connection statuses are disconnected, connected, requested"""

    connection_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    competitor_inn = db.Column(db.Integer, nullable=False)
    competitor_nickname = db.Column(db.String(100))
    competitor_website = db.Column(db.String(200))
    connection_status = db.Column(
        db.String(200), default="disconnected", nullable=False
    )


class Scrapers(db.Model):
    """Stores paths to the companies websites scrapers.
    For each company there can be only 1 scraper file to save storage space and not
    write the same web scraper twice"""

    scraper_id = db.Column(db.Integer, primary_key=True)
    company_inn = db.Column(db.Integer, nullable=False)
    scraper_path = db.Column(db.String(200), nullable=False)


class UsersItems(db.Model):
    """Stores all the  unique connections between users and theis items.
    When an item gets deleted, it gets deleted only here"""

    connection_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(200), nullable=False, unique=True)


class ItemsRecords(db.Model):
    """Stores all the records of items' prices.
    Nothing ever gets deleted from this table."""

    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(300), nullable=False)
    company_inn = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(200), nullable=False)


class ItemsConnections(db.Model):
    """Stores connections between items.
    Records keep existing even when the item is deleted in case the user
    restores it or for other future features"""

    connection_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_link = db.Column(db.String(200), nullable=False)
    connected_item_link = db.Column(db.String(200), nullable=False)
