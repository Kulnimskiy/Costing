import logging
import decimal
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from project.helpers import inn_checker, format_search_all_result, check_price, unhash_inn, get_link, get_cur_date
from project.request_connection import send_connect_request
from project.async_search import run_search_link, run_search_all_items, run_search_all_links
from project.db_manager import load_company_data, db_add_competitor, db_get_competitors, db_delete_competitor, \
    db_get_competitor, db_update_con_status, db_add_scraper, db_add_item, db_get_items, db_add_refreshed_item, \
    db_delete_item_connection, db_get_user_website, db_change_website

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def index():
    # get the info about the user from the obj current_user like current_user._id
    _inn = current_user.company_inn
    user_id = current_user.get_id()
    company_info = load_company_data(_inn)
    if company_info:
        requested_connection = db_get_competitor(user_id=user_id, com_inn=_inn)

        # The user can change the website if he hasn't requested the connection yet
        if requested_connection:
            website = {"link": get_link(requested_connection.competitor_website),
                       "status": requested_connection.connection_status}
            return render_template("homepage.html", user=current_user, company_info=company_info, website=website)
        website = {"link": get_link(company_info.website), "status": "disconnected"}
        return render_template("homepage.html", user=current_user, company_info=company_info, website=website)
    return render_template("homepage.html", user=current_user, company_info=company_info)


@main.route("/profile")
@login_required
def profile():
    _inn = current_user.company_inn
    user_id = current_user.get_id()
    company_info = load_company_data(_inn)
    if company_info:
        requested_connection = db_get_competitor(user_id=user_id, com_inn=_inn)

        # The user can change the website if he hasn't requested the connection yet
        if requested_connection:
            website = {"link": get_link(requested_connection.competitor_website),
                       "status": requested_connection.connection_status}
            return render_template("profile.html", user=current_user, company_info=company_info, website=website)
        website = {"link": get_link(company_info.website), "status": "disconnected"}
        return render_template("profile.html", user=current_user, company_info=company_info, website=website)
    return render_template("profile.html")


@main.route("/company-goods", methods=["POST", "GET"])
@login_required
def company_goods():
    user_id = current_user.get_id()
    available_competitors = db_get_competitors(current_user.get_id(), "connected")
    items = db_get_items(user_id)
    if request.method == "POST":
        item_link = get_link(request.form.get("item_link"))
        if not item_link:
            return render_template("company-goods.html", competitors=available_competitors, items=items)
        competitor_inn = None
        for competitor in available_competitors:
            if competitor.competitor_website in item_link:
                competitor_inn = competitor.competitor_inn
        if not competitor_inn or competitor_inn not in [competitor.competitor_inn for competitor in
                                                        available_competitors]:
            return render_template("company-goods.html", competitors=available_competitors, items=items)
        item = db_add_item(user_id, competitor_inn, item_link)
        if not item:
            print("there is no such item")
            return render_template("company-goods.html", competitors=available_competitors, items=items)
        items = db_get_items(user_id)
    return render_template("company-goods.html", competitors=available_competitors, items=items)


@main.route("/company-goods/refresh_all")
@login_required
def refresh_item_prices():
    user_id = current_user.get_id()
    available_competitors = db_get_competitors(user_id, "connected")
    items = db_get_items(user_id)
    links = []
    for item in items:
        for competitor in available_competitors:
            if competitor.competitor_website in item["link"]:
                links.append((competitor.competitor_inn, item["link"]))
    results = run_search_all_links(user_id, links)
    date = get_cur_date()
    for result in results:
        if result:
            for link in links:
                if link[1] == result["url"]:
                    db_add_refreshed_item(item_name=result["name"],
                                          company_inn=link[0],
                                          link=result["url"],
                                          price=result["price"],
                                          date=date)
        else:
            logging.warning("Item not added")
    return redirect("/company-goods")


@main.route("/company-goods/delete-item", methods=["POST"])
@login_required
def delete_item():
    item_id = request.form.get("item_id")
    user_id = current_user.get_id()
    print(item_id)
    if db_delete_item_connection(user_id, item_id):
        return redirect("/company-goods")
    logging.warning("Item is not deleted. Access denied")
    return redirect("/company-goods")


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
            return render_template("price-looker.html", competitors=available_competitors)

        min_price = check_price(request.form.get("min_price"))
        max_price = check_price(request.form.get("max_price"))
        result = run_search_all_items(current_user.get_id(), item=item, chosen_comps=chosen_competitors)
        result = format_search_all_result(item, result, available_competitors, min_price, max_price)
        return render_template("price-looker-results.html", items=result)
    if request.method == "GET":
        item_search_field = request.args.get("item-search-field")

        if item_search_field:
            chosen_comps = [str(cls.competitor_inn) for cls in available_competitors]
            result = run_search_all_items(current_user.get_id(), item=item_search_field,
                                          chosen_comps=chosen_comps)
            result = format_search_all_result(item_search_field, result, available_competitors)
            return render_template("price-looker_layout.html", competitors=available_competitors,
                                   items=result)
    return render_template("price-looker.html", competitors=available_competitors)


@main.route("/profile/delete_competitor/<com_inn>", methods=["POST"])
@login_required
def delete_competitor(com_inn):
    com_inn = inn_checker(com_inn)
    db_delete_competitor(user_id=current_user.get_id(), com_inn=com_inn)
    return redirect(url_for("main.competitor_monitoring"))


@main.route("/request_connection/<com_inn>", methods=["POST"])
@login_required
def request_connection(com_inn):
    user_id = current_user.get_id()
    com_inn = inn_checker(com_inn)
    competitor = db_get_competitor(user_id=user_id, com_inn=com_inn)
    if db_update_con_status(user_id, com_inn):
        send_connect_request(current_user, competitor)
        return redirect(url_for("main.competitor_monitoring"))
    return redirect(url_for("main.competitor_monitoring"))


@main.route("/profile/change_web", methods=["GET", "POST"])
def change_web():
    user_id = current_user.get_id()
    _inn = current_user.company_inn
    available_inns = [competitor.competitor_inn for competitor in db_get_competitors(user_id)]
    available_inns.append(_inn)
    new_web = request.form.get("new_web")

    # if addressed directly
    if request.method == "GET":
        comp_inn = inn_checker(request.args.get("inn"))
        if comp_inn not in available_inns or not new_web:
            return redirect("/competitor-monitoring")
        requested_connection = db_get_competitor(user_id=user_id, com_inn=comp_inn)
        if not requested_connection or requested_connection.connection_status == "disconnected":
            if db_change_website(user_id, _inn, new_website=new_web):
                return redirect("/competitor-monitoring")
            else:
                return redirect("/competitor-monitoring")

    comp_inn = inn_checker(request.form.get("inn"))
    if comp_inn not in available_inns:
        return "Not allowed"
    if not new_web:
        return "Empty field"
    requested_connection = db_get_competitor(user_id=user_id, com_inn=comp_inn)
    if not requested_connection or requested_connection.connection_status == "disconnected":
        if db_change_website(user_id, _inn, new_website=new_web):
            return new_web
        else:
            return "Something went wrong"
    return f"Not valid: {new_web}"
