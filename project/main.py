from flask import Blueprint, render_template
from . import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("homepage.html")


@main.route("/profile")
def profile():
    return "Company profile"


@main.route("/company-goods")
def profile():
    return "Company’s goods and prices"


@main.route("/competitor-monitoring")
def profile():
    return "Competitors and their monitored goods"


@main.route("/comparison")
def profile():
    return "Comparison of the prices between you and your competitors"


@main.route("/price-looker")
def profile():
    return "Company profile"
