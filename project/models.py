from . import db
from flask_login import UserMixin


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

