import logging
import time
from random import randint
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from project.helpers import inn_checker, format_search_all_result, check_price, compare_names, get_item_model
from project.database import CompanyDB, CompetitorDB, ItemDB, RelationsDB, ScraperDB
from project.emails import EmailTemplates
from project.async_search import run_search_all_items, run_search_all_links, run_search_item
from project.db_manager import *
from project.credentials import MIN_RELEVANCE, ITEMS_UPDATE_TIMEOUT_RANGE
from project.managers import UrlManager, InnManager

main = Blueprint("main", __name__)


@main.get("/")
@login_required
def index():
    # get the info about the user from the obj current_user like current_user._id
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    user_company = CompanyDB(user_inn).load()
    if user_company is None:
        return render_template("homepage.html", user=current_user)

    # the user company is also a competitor if he has ever requested a connection
    user_as_cp = CompetitorDB(user_id, user_inn).get()

    # The user can change the website if he hasn't requested the connection yet
    if user_as_cp:
        website = {"link": user_as_cp.competitor_website, "status": user_as_cp.connection_status}
        return render_template("homepage.html", user=current_user, company_info=user_company, website=website)

    website = {"link": get_link(user_company.website), "status": "disconnected"}
    return render_template("homepage.html", user=current_user, company_info=user_company, website=website)


@main.get("/profile")
@login_required
def get_profile():
    """ Get the profile with all the existing items """
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    company_info = CompanyDB(user_inn).load()
    competitors = CompetitorDB.get_all(user_id, connection_status=CompetitorDB.CONNECTION_STATUS[1])

    # remove the current user from the competitors list
    competitors = [competitor for competitor in competitors if competitor.competitor_inn != current_user.company_inn]

    # get related items in the right format
    formatted_relations = RelationsDB.get_format_all(user_id, user_inn)
    user_as_cp = CompetitorDB(user_id, user_inn).get()
    if not company_info:
        logging.warning(f"THERE WAS NO COMPANY INFO ON {user_inn}")
        return render_template("profile.html",
                               competitors=competitors,
                               items_info=formatted_relations,
                               user_con=user_as_cp)

    # The user can change the website if he hasn't requested the connection yet
    if user_as_cp:
        website = {"link": UrlManager(user_as_cp.competitor_website).check(),
                   "status": user_as_cp.connection_status}
    else:
        website = {"link": UrlManager(company_info.website).check(), "status": "disconnected"}
    return render_template("profile.html", user=current_user, company_info=company_info,
                           website=website, competitor=user_as_cp, competitors=competitors,
                           items_info=formatted_relations, user_con=user_as_cp)


@main.post("/profile")
@login_required
def post_profile():
    _inn = current_user.company_inn
    user_id = current_user.get_id()
    user_con = db_get_competitor(user_id, _inn)
    if request.method == "POST":
        # here u don't have to check if the user's web is connected
        item_name = request.form.get("item_name")
        if not item_name:
            return redirect("/profile")
        item_price = check_price(request.form.get("item_price"))
        if not item_price:
            return redirect("/profile")
        item_link = get_link(request.form.get("item_link"))
        if not item_link:
            item_link = db_get_item_link_new(user_id=user_id, company_inn=_inn, item_name=item_name)
        db_add_item_mnl(user_id=user_id,
                        company_inn=_inn,
                        item_name=item_name,
                        price=item_price,
                        link=item_link)
        logging.warning("ITEM HAS BEEN ADDED MANUALLY")


@main.post("/profile/load_item")
@login_required
def load_user_item():
    """ load only user's own items from his web """
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    user_con = CompetitorDB(user_id, user_inn).get()
    if not user_con or user_con.connection_status != "connected":
        return redirect(url_for("main.profile"))
    item_link = get_link(request.form.get("main.get_profile"))
    if not item_link:
        print("No link")
        return redirect(url_for("main.get_profile"))
    if user_con.competitor_website not in item_link:
        print("wrong link")
        return redirect(url_for("main.get_profile"))
    ItemDB(user_id, item_link).update()
    logging.warning("ITEM HAS BEEN ADDED FROM THE WEB")
    return redirect(url_for("main.get_profile"))


@main.route("/company-goods", methods=["POST", "GET"])
@login_required
def company_goods():
    user_id = current_user.get_id()
    available_competitors = CompetitorDB.get_all(user_id, "connected")
    items = ItemDB.get_format_all(user_id)

    if request.method == "POST":  # in case we decide to add an item
        item_link = UrlManager(request.form.get("item_link")).check()
        if not item_link:
            return render_template("company-goods.html", competitors=available_competitors, items=items)

        item = ItemDB(user_id, item_link).update()
        if not item:
            logging.warning("THERE IS NO SUCH ITEM TO ADD TO YOUR ITEM LIST")
            return render_template("company-goods.html", competitors=available_competitors, items=items)
        items = ItemDB.get_format_all(user_id)

    return render_template("company-goods.html", competitors=available_competitors, items=items)


@main.get("/company-goods/refresh_all")
@login_required
def refresh_item_prices():
    user_id = current_user.get_id()
    available_competitors = CompetitorDB.get_all(user_id, "connected")
    items = ItemDB.get_format_all(user_id)
    links = []
    for item in items:
        for competitor in available_competitors:
            if competitor.competitor_website in item["link"]:
                links.append((competitor.competitor_inn, item["link"]))
    results = run_search_all_links(user_id, links)
    for result in results:
        if result:
            for link in links:
                if link[1] == result["url"]:
                    ItemDB(user_id, result["url"]).create(item_name=result["name"], item_price=result["price"])
        else:
            logging.warning(F"ITEM {result['url']} WASN'T UPDATED")
    logging.warning("THE ITEMS HAVE BEEN UPDATED")
    return redirect("/company-goods")


@main.post("/company-goods/delete-item")
@login_required
def delete_item():
    item_id = request.form.get("item_id")
    user_id = current_user.get_id()
    item = ItemDB.get_by_id(user_id, item_id)
    if not item:
        logging.warning("THERE IS NO SUCH ITEM")
        return redirect("/company-goods")
    if ItemDB(user_id, item.link).delete():
        if "profile" in request.referrer:
            return redirect(url_for("main.get_profile"))
        return redirect("/company-goods")
    logging.warning("Item is not deleted. Access denied")
    return redirect("/company-goods")


@main.get("/competitor-monitoring")
@login_required
def get_competitor_monitoring():
    competitors = CompetitorDB.get_all(current_user.get_id())
    competitors = [competitor for competitor in competitors if competitor.competitor_inn != current_user.company_inn]
    return render_template("competitor-monitoring.html", competitors=competitors)


@main.post("/competitor-monitoring")
@login_required
def post_competitor_monitoring():
    user_id = current_user.get_id()
    cp_inn = InnManager(request.form.get("inn")).check()
    if not cp_inn:
        logging.warning("PROVIDED INN IS NOT VALID")
        return redirect("/competitor-monitoring")
    company = request.form.get("company")
    website = UrlManager(request.form.get("website")).check()
    CompetitorDB(user_id, cp_inn).create(cp_nickname=company, website=website)
    ScraperDB(user_id, cp_inn).create()  # create a scraper for the company
    return redirect("/competitor-monitoring")


@main.route("/comparison")
@login_required
def comparison():
    """Compare prices of the user's items and his competitors(cr)"""
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    all_crs = CompetitorDB.get_all(user_id=user_id, connection_status="connected")

    # get rid of the user from the competitors list
    crs = [cr for cr in all_crs if cr.competitor_inn != user_inn]
    all_items = db_get_items(user_id)
    own_items = list(filter(lambda x: inn_checker(x["competitor_inn"]) == user_inn, all_items))

    items_info = RelationsDB.get_format_compare(user_id, user_inn)

    return render_template("comparison.html", items=own_items, items_info=items_info, competitors=crs)


@main.route("/price-looker", methods=["GET", "POST"])
@login_required
def price_looker():
    user_id = current_user.get_id()
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
        for r in result:
            if db_get_item(user_id, r["url"]):
                r["added"] = True
            else:
                r["added"] = False
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
    return render_template("price-looker.html", competitors=available_competitors, user_inn=current_user.company_inn)


@main.route("/profile/delete_competitor/<com_inn>", methods=["POST"])
@login_required
def delete_competitor(com_inn):
    user_id = current_user.get_id()
    cp_inn = InnManager(com_inn).check()
    CompetitorDB(user_id, cp_inn=cp_inn).delete()
    if "profile" in request.referrer:
        return redirect(url_for("main.get_profile"))
    return redirect(url_for("main.get_competitor_monitoring"))


@main.route("/request_connection/<com_inn>", methods=["POST"])
@login_required
def request_connection(com_inn):
    user_id = current_user.get_id()
    com_inn = inn_checker(com_inn)
    competitor = db_get_competitor(user_id=user_id, com_inn=com_inn)
    if not competitor:
        company = load_company_data(com_inn)
        db_change_website(user_id, com_inn, new_website=company.website)
        competitor = db_get_competitor(user_id=user_id, com_inn=com_inn)
    if db_update_con_status(user_id, com_inn):
        EmailTemplates.request_connect(current_user, competitor)
        db_add_scraper(user_inn=current_user.company_inn, comp_inn=current_user.company_inn)
        print("scr made")
        if "profile" in request.referrer:
            return redirect(url_for("main.profile"))
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


@main.route("/profile/link_items", methods=["POST"])
@login_required
def link_items():
    user_id = current_user.get_id()
    item_id = check_price(request.form.get("item_id"))
    if not item_id:
        return "No item"
    item_link = db_get_item_link(user_id=user_id, item_id=item_id)
    if not item_link:
        return "You don't have this item"
    comp_inn = inn_checker(request.form.get("comp_inn"))
    if not comp_inn:
        return "This comp isn't added"
    available_inns = [competitor.competitor_inn for competitor in
                      db_get_competitors(user_id, connection_status="connected")]
    if comp_inn not in available_inns:
        return "This comp isn't connected"
    new_link = get_link(request.form.get("new_link"))
    old_link = db_get_item_connection(user_id=user_id, user_link=item_link, comp_inn=comp_inn)
    if not new_link:
        if old_link:
            db_delete_connection(user_id=user_id, item_link=item_link, linked_item_link=old_link.connected_item_link)
        return "deleted"
    if not db_add_item(user_id=user_id, company_inn=comp_inn, link=new_link):
        return "Cannot get item info!"
    if db_add_item_connection(user_id=user_id, item_link=item_link, connected_item_link=new_link, comp_inn=comp_inn):
        print(item_link, "connected to ", new_link)
        return new_link
    return old_link.connected_item_link if old_link else "Wrong inn or same link"


@main.route("/items_owned")
def items_owned():
    """ Returns a list of items owned by user"""
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    all_items = db_get_items(user_id)
    own_items = list(filter(lambda x: inn_checker(x["competitor_inn"]) == user_inn, all_items))
    # json_items = json.dumps(own_items)
    search = request.args.get('term')
    if not search:
        return {"0": "Nothing will connect"}
    resp = list(filter(lambda x: search.lower() in x["name"].lower(), own_items))
    return resp


@main.route("/autoload_associations", methods=["POST"])
def autoload_associations():
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    all_items = db_get_items(user_id)
    own_items = list(filter(lambda x: inn_checker(x["competitor_inn"]) == user_inn, all_items))
    phrase = "Комплект Rextar X и Kodak RVG 6200 - высокочастотный портативный дентальный рентген с визиографом"
    # title_compare(phrase, own_items)
    # the approximate result relevance minimum is 0.37. If there are more than 1, get the highest
    competitors = db_get_competitors(current_user.get_id())
    competitors_inn = [str(competitor.competitor_inn) for competitor in competitors if
                       competitor.competitor_inn != current_user.company_inn]
    lst_relevant = dict()
    for item in own_items:
        time.sleep(randint(1, ITEMS_UPDATE_TIMEOUT_RANGE))

        # searches the item only among the competitors the item doesn't have a connection with
        all_inns = competitors_inn.copy()
        available_inns = competitors_inn.copy()
        for inn in all_inns:
            if db_get_item_connection(user_id=user_id, user_link=item["link"], comp_inn=inn):
                available_inns.remove(inn)

        search = run_search_all_items(user_id, item["name"], available_inns)
        item_con = dict()
        model = get_item_model(item["name"])
        if not search and model:
            search = run_search_all_items(user_id, item["name"], available_inns)
        if not search:
            continue
        for result in search:
            competitor_inn = db_get_inn(user_id, result["url"])
            if str(competitor_inn) in available_inns:
                available_inns.remove(str(competitor_inn))
            result["relevance"] = compare_names(item["name"], result["name"])
            last_relevance = item_con[competitor_inn]["relevance"] if item_con.get(competitor_inn) else 0
            if result["relevance"] > MIN_RELEVANCE and result["relevance"] >= last_relevance:
                item_con[competitor_inn] = result
                continue

        # if any of the comps hasn't given the answer, try searching by the model
        if available_inns:
            for inn in available_inns:
                search_again = run_search_item(user_id, inn, model)
                if not search_again:
                    continue
                for result in search_again:
                    competitor_inn = db_get_inn(user_id, result["url"])
                    result["relevance"] = compare_names(item["name"], result["name"])
                    last_relevance = item_con[competitor_inn]["relevance"] if item_con.get(competitor_inn) else 0
                    if result["relevance"] > MIN_RELEVANCE and result["relevance"] >= last_relevance:
                        item_con[competitor_inn] = result
                        continue
        lst_relevant[item["link"]] = item_con
    if lst_relevant:
        for item_link, connections in lst_relevant.items():
            if connections:
                for cp_inn, cp_item in connections.items():
                    db_add_item(user_id, cp_inn, cp_item["url"])
                    db_add_item_connection(user_id, item_link, cp_item["url"], cp_inn)
    # db_add_item_connection(user_id, item["link"], result["url"])
    return redirect("/profile")
