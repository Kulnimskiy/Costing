import html

from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from project.helpers import inn_checker, format_search_all_result, check_price, unhash_inn
from project.request_connection import send_connect_request
from project.corpotate_scrapers.stomart_async import run_search_all
from project.async_search import run_search_item, run_search_link, run_search_all_items, run_search_all_links
from project.db_manager import load_company_data, db_add_competitor, db_get_competitors, db_delete_competitor, \
    db_get_competitor, db_update_con_status, db_add_scraper

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
        db_add_competitor(user_id=current_user.get_id(), comp_inn=_inn, comp_nickname=company, website=website)
        db_add_scraper(user_inn=current_user.company_inn, comp_inn=_inn)
        competitors = db_get_competitors(current_user.get_id())
        return render_template("competitor-monitoring.html", competitors=competitors)
    competitors = db_get_competitors(current_user.get_id())
    return render_template("competitor-monitoring.html", competitors=competitors)


@main.route("/comparison")
@login_required
def comparison():
    return "Comparison of the prices between you and your competitors"


@main.route("/price-looker", methods=["GET", "POST"])
@login_required
def price_looker():
    available_competitors = db_get_competitors(current_user.get_id(), "connected")
    if request.method == "POST":
        # returns a html table with search results for ajax
        item = request.form.get("item")
        if not item:
            return render_template("price-looker-results.html", competitors=available_competitors)

        #  if no one has been chosen the search uses all of competitors
        chosen_competitors = request.form.getlist("chosen_competitor")
        if not chosen_competitors:
            chosen_competitors = available_competitors

        min_price = check_price(request.form.get("min_price"))
        max_price = check_price(request.form.get("max_price"))
        result = run_search_all_items(current_user.get_id(), item=item, chosen_comps=chosen_competitors)
        result = format_search_all_result(item, result, min_price, max_price)
        return render_template("price-looker-results.html", items=result)
    if request.method == "GET":
        item_search_field = request.args.get("item-search-field")

        if item_search_field:
            chosen_comps = [str(cls.competitor_inn) for cls in available_competitors]
            result = run_search_all_items(current_user.get_id(), item=item_search_field,
                                          chosen_comps=chosen_comps)
            result = format_search_all_result(item_search_field, result)
            return render_template("price-looker_layout.html", competitors=available_competitors,
                                   items=result)
    return render_template("price-looker.html", competitors=available_competitors)


@main.route("/profile/delete_competitor/<com_inn>", methods=["POST"])
def delete_competitor(com_inn):
    com_inn = inn_checker(com_inn)
    db_delete_competitor(user_id=current_user.get_id(), com_inn=com_inn)
    return redirect(url_for("main.competitor_monitoring"))


@main.route("/request_connection/<com_inn>", methods=["POST"])
def request_connection(com_inn):
    user_id = current_user.get_id()
    com_inn = inn_checker(com_inn)
    competitor = db_get_competitor(user_id=user_id, com_inn=com_inn)
    if db_update_con_status(user_id, com_inn):
        send_connect_request(current_user, competitor)
        return redirect(url_for("main.competitor_monitoring"))
    return redirect(url_for("main.competitor_monitoring"))

# @main.route("/test")
# def test():
#     funk()
#     return redirect("/")
