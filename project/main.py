from flask import Blueprint, render_template, session, redirect
from . import db

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if session.get("user") is None:
        return redirect("/login")
    return render_template("homepage.html")


@main.route("/profile")
def profile():
    return "Company profile"


@main.route("/company-goods")
def company_goods():
    return "Company’s goods and prices"


@main.route("/competitor-monitoring")
def competitor_monitoring():
    return "Competitors and their monitored goods"


@main.route("/comparison")
def comparison():
    return "Comparison of the prices between you and your competitors"


@main.route("/price-looker")
def price_looker():
    return "Company profile"
