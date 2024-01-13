from flask import Blueprint, render_template, session, redirect, request
from flask_login import login_required, current_user
from .db_manager import load_company_data, db_add_competitor, db_get_competitors
from .helpers import inn_checker
main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    # get the info about the user from the obj current_user like current_user._id
    _inn = current_user.company_inn
    company_info = load_company_data(_inn)
    if company_info:
        weblink_title = company_info.website
        website_link = "https://" + weblink_title if weblink_title else None
        return render_template("homepage.html", user=current_user, company_info=company_info, website=website_link)
    return render_template("homepage.html", user=current_user, company_info=company_info)


@main.route("/profile")
@login_required
def profile():
    return "Company profile"


@main.route("/company-goods")
@login_required
def company_goods():
    return "Company’s goods and prices"


@main.route("/competitor-monitoring", methods=["GET", "POST"])
@login_required
def competitor_monitoring():
    if request.method == "POST":
        _inn = inn_checker(request.form.get("inn"))
        company = request.form.get("company")
        website = request.form.get("website")
        db_add_competitor(current_user.company_inn, comp_inn=_inn, comp_nickname=company, website=website)
        competitors = db_get_competitors(current_user.company_inn)
        return render_template("competitor-monitoring.html", competitors=competitors)
    competitors = db_get_competitors(current_user.company_inn)
    return render_template("competitor-monitoring.html", competitors=competitors)


@main.route("/comparison")
@login_required
def comparison():
    return "Comparison of the prices between you and your competitors"


@main.route("/price-looker")
@login_required
def price_looker():
    return "Company profile"
