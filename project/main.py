from flask import Blueprint, render_template, session, redirect
from flask_login import login_required, current_user
from . import db
from .web_scrapers.company_info_search import Company

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    print(current_user.__dict__)
    company = Company(current_user.company_inn)
    company_info = company.get_full_info()
    website_link = "http://" + company_info["website"] if company_info["website"] else None
    # get the info about the user from the obj current_user like current_user._id
    return render_template("homepage.html", user=current_user, company_info=company_info, website=website_link)


@main.route("/profile")
@login_required
def profile():
    return "Company profile"


@main.route("/company-goods")
@login_required
def company_goods():
    return "Company’s goods and prices"


@main.route("/competitor-monitoring")
@login_required
def competitor_monitoring():
    return "Competitors and their monitored goods"


@main.route("/comparison")
@login_required
def comparison():
    return "Comparison of the prices between you and your competitors"


@main.route("/price-looker")
@login_required
def price_looker():
    return "Company profile"
