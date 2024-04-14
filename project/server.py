import time
import logging
from random import randint
from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from project.database import CompanyDB, CompetitorDB, ItemDB, RelationsDB, ScraperDB, UserDB
from project.emails import EmailTemplates
from project.search_files.async_search import run_search_all_items, run_search_all_links, run_search_item
from project.credentials import MIN_RELEVANCE, ITEMS_UPDATE_TIMEOUT_RANGE
from project.managers import UrlManager, InnManager, PriceManager, EmailManager
from project.helpers import ResultFormats, OperationalTools, ItemName

main = Blueprint("main", __name__)


@main.get("/")
@login_required
def index():
    # get the info about the user from the obj current_user like current_user._id
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    user_company = CompanyDB(user_inn).load()
    if user_company is None:
        return render_template("homepage.html", user=current_user, company_info=dict(), website=None)

    # the user company is also a competitor if he has ever requested a connection
    user_as_cp = CompetitorDB(user_id, user_inn).get()

    # The user can change the website if he hasn't requested the connection yet
    if user_as_cp:
        website = {"link": user_as_cp.competitor_website, "status": user_as_cp.connection_status}
        return render_template("homepage.html", user=current_user, company_info=user_company, website=website)

    website = {"link": UrlManager(user_company.website).check(), "status": "disconnected"}
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
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    item_name = request.form.get("item_name")
    if not item_name:
        return redirect("/profile")
    item_price = PriceManager(request.form.get("item_price")).check()
    if not item_price:
        return redirect("/profile")
    item_link = UrlManager(request.form.get("item_link")).check()
    if not item_link:
        item_link = ItemDB.generate_url(user_id=user_id, company_inn=user_inn, item_name=item_name)
    ItemDB(user_id=user_id, url=item_link).create(item_name=item_name, item_price=item_price)
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
    item_link = UrlManager(request.form.get("item_link")).check()
    if not item_link:
        print("No link")
        return redirect(url_for("main.get_profile"))
    if user_con.competitor_website not in item_link:
        print(item_link, user_con.competitor_website)
        print("wrong link")
        return redirect(url_for("main.get_profile"))
    ItemDB(user_id, item_link).update()
    logging.warning("ITEM HAS BEEN ADDED FROM THE WEB")
    return redirect(url_for("main.get_profile"))


@main.get("/company-goods")
@login_required
def company_goods_get():
    user_id = current_user.get_id()
    available_competitors = CompetitorDB.get_all(user_id, "connected")
    items = ItemDB.get_format_all(user_id)
    return render_template("company-goods.html", competitors=available_competitors, items=items)


@main.post("/company-goods")
@login_required
def company_goods_post():
    """ In case we decide to add items from the profile page """
    user_id = current_user.get_id()
    item_link = UrlManager(request.form.get("item_link")).check()
    if not item_link:
        return redirect(url_for("main.company_goods_get"))

    item = ItemDB(user_id, item_link).update()
    if not item:
        logging.warning("THERE IS NO SUCH ITEM TO ADD TO YOUR ITEM LIST")
        return redirect(url_for("main.company_goods_get"))
    return redirect(url_for("main.company_goods_get"))


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
            logging.warning(f"ITEM {result['url']} WASN'T UPDATED")
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
    all_items = ItemDB.get_format_all(user_id)
    own_items = list(filter(lambda x: InnManager(x["competitor_inn"]).check() == str(user_inn), all_items))

    items_info = RelationsDB.get_format_compare(user_id, user_inn)

    return render_template("comparison.html", items=own_items, items_info=items_info, competitors=crs)


@main.get("/price-looker")
@login_required
def price_looker_get():
    """ The page you go to from the nav bar """
    user_id = current_user.get_id()
    available_competitors = CompetitorDB.get_all(user_id=user_id, connection_status="connected")
    item_search_field = request.args.get("item-search-field")
    if not item_search_field:
        return render_template("price-looker.html",
                               competitors=available_competitors,
                               user_inn=current_user.company_inn)
    chosen_comps = [str(cls.competitor_inn) for cls in available_competitors]
    result = run_search_all_items(current_user.get_id(), item=item_search_field, chosen_comps=chosen_comps)
    result = ResultFormats.search_all_result(item_search_field, result, available_competitors)
    return render_template("price-looker_layout.html", competitors=available_competitors, items=result)


@main.post("/price-looker")
@login_required
def price_looker_post():
    """ Returns a html table with search results for ajax request from the frontend """
    user_id = current_user.get_id()
    available_competitors = CompetitorDB.get_all(user_id=user_id, connection_status="connected")

    item = request.form.get("item")
    if not item:
        return redirect("/price_looker")

    #  if no one has been chosen the search uses all of competitors
    chosen_competitors = request.form.getlist("chosen_competitor")
    if not chosen_competitors:
        return redirect("/price_looker")

    min_price = PriceManager(request.form.get("min_price")).check()
    max_price = PriceManager(request.form.get("max_price")).check()
    results = run_search_all_items(current_user.get_id(), item=item, chosen_comps=chosen_competitors)
    results_formatted = ResultFormats.search_all_result(item, results, available_competitors, min_price, max_price)

    # if the item is already in the db, we mark it as added to show that to the user
    for result in results_formatted:
        if ItemDB(user_id, result["url"]).get():
            result["added"] = True
        else:
            result["added"] = False
    return render_template("price-looker-results.html", items=results)


@main.route("/profile/delete_competitor/<com_inn>", methods=["POST"])
@login_required
def delete_competitor(com_inn):
    user_id = current_user.get_id()
    cp_inn = InnManager(com_inn).check()
    CompetitorDB(user_id, cp_inn=cp_inn).delete()
    if "profile" in request.referrer:
        return redirect(url_for("main.get_profile"))
    return redirect(url_for("main.get_competitor_monitoring"))


@main.route("/request_connection/<cp_inn>", methods=["POST"])
@login_required
def request_connection(cp_inn):
    """ Used to send a request connection email to Admin to start working on a scraper """
    user_id = current_user.get_id()
    cp_inn = InnManager(cp_inn).check()
    if not cp_inn:
        logging.warning("THE COMPETITOR INN IS NOT VALID")
        redirect(url_for("main.get_competitor_monitoring"))

    competitor = CompetitorDB(user_id=user_id, cp_inn=cp_inn)
    if not competitor.get():  # that means that the user tries to connect his website
        competitor.create()  # create the competitor in the db and his scraper file

    if competitor.update_status(new_status="requested"):
        competitor = competitor.get()
        EmailTemplates.request_connect(current_user, competitor)
        if "profile" in request.referrer:
            return redirect(url_for("main.get_profile"))
        return redirect(url_for("main.get_competitor_monitoring"))
    return redirect(url_for("main.get_competitor_monitoring"))


@main.post("/profile/change_web")
def change_web_post():
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    available_inns = [competitor.competitor_inn for competitor in CompetitorDB.get_all(user_id)]
    available_inns.append(user_inn)
    new_web = UrlManager(request.form.get("new_web")).check()
    cp_inn = InnManager(request.form.get("inn")).check()
    if cp_inn not in available_inns:
        return "Not allowed"
    if not new_web:
        return "Empty field"
    requested_connection = CompetitorDB(user_id=user_id, cp_inn=cp_inn).get()
    if not requested_connection or requested_connection.connection_status == "disconnected":
        if UserDB(user_id).change_web(new_website=new_web):
            return new_web
        else:
            return "Something went wrong"
    return f"Not valid: {new_web}"


@main.get("/profile/change_web")
def change_web_get():
    """ Changes user's website if the user has not requested a connection ever """
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    available_inns = [competitor.competitor_inn for competitor in CompetitorDB.get_all(user_id)]
    available_inns.append(user_inn)

    cp_inn = InnManager(request.args.get("inn")).check()
    new_web = UrlManager(request.form.get("new_web")).check()

    if cp_inn not in available_inns or not new_web:
        return redirect("/competitor-monitoring")

    requested_connection = CompetitorDB(user_id=user_id, cp_inn=cp_inn).get()
    if not requested_connection or requested_connection.connection_status == "disconnected":
        UserDB(user_id).change_web(new_website=new_web)
    return redirect("/competitor-monitoring")


@main.post("/profile/change_email")
def change_email_post():
    user_id = current_user.get_id()
    new_email = EmailManager(request.form.get("new_email")).check()
    if not new_email:
        return "Error"
    if UserDB(user_id).change_email(new_email):
        return new_email
    return "Error"


@main.route("/profile/link_items", methods=["POST"])
@login_required
def link_items():
    user_id = current_user.get_id()
    item_id = OperationalTools.check_int(request.form.get("item_id"))
    if not item_id:
        return "No item"
    item = ItemDB.get_by_id(user_id=user_id, item_id=item_id)
    if not item:
        return "You don't have this item"
    item_link = item.link
    cp_inn = InnManager(request.form.get("comp_inn")).check()
    if not cp_inn:
        return "This comp isn't added"
    available_competitors = CompetitorDB.get_all(user_id, connection_status="connected")
    available_inns = [competitor.competitor_inn for competitor in available_competitors]
    if cp_inn not in available_inns:
        return "This comp isn't connected"
    new_link = UrlManager(request.form.get("new_link")).check()
    item_connection = RelationsDB(user_id=user_id, item_url=item_link)
    old_item_record = RelationsDB(user_id=user_id, item_url=item_link).get_by_inn(cp_inn=cp_inn)
    if not new_link:
        if old_item_record:
            item_connection.delete_relation(related_item_url=old_item_record.connected_item_link)
        return "deleted"
    if not ItemDB(user_id=user_id, url=new_link).update():
        return "Cannot get item info!"
    if item_connection.create_relation(related_item_url=new_link, cp_inn=cp_inn):
        logging.warning(item_link + "connected to " + new_link)
        return new_link
    return old_item_record.connected_item_link if old_item_record else "Wrong inn or same link"


@main.route("/items_owned")
def items_owned():
    """ Returns a list of items owned by user"""
    user_id = current_user.get_id()
    user_inn = current_user.company_inn
    all_items = ItemDB.get_format_all(user_id)
    own_items = list(filter(lambda x: InnManager(x["competitor_inn"]).check() == user_inn, all_items))
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
    all_items = ItemDB.get_format_all(user_id)
    own_items = list(filter(lambda x: InnManager(x["competitor_inn"]).check() == str(user_inn), all_items))

    # the approximate result relevance minimum is 0.37. If there are more than 1, get the highest
    competitors = CompetitorDB.get_all(current_user.get_id())
    competitors_inn = [str(competitor.competitor_inn) for competitor in competitors if
                       competitor.competitor_inn != current_user.company_inn]
    lst_relevant = dict()
    for item in own_items:
        time.sleep(randint(1, ITEMS_UPDATE_TIMEOUT_RANGE))

        # searches the item only among the competitors the item doesn't have a connection with
        all_inns = competitors_inn.copy()
        available_inns = competitors_inn.copy()
        for inn in all_inns:
            if RelationsDB(user_id=user_id, item_url=item["link"]).get_by_inn(cp_inn=inn):
                available_inns.remove(inn)

        search = run_search_all_items(user_id, item["name"], available_inns)
        item_con = dict()
        item_name = ItemName(item["name"])
        model = item_name.get_model()
        if not search and model:
            search = run_search_all_items(user_id, item["name"], available_inns)
        if not search:
            continue
        for result in search:
            competitor_inn = ItemDB(user_id, result["url"]).get_cp_inn()
            if str(competitor_inn) in available_inns:
                available_inns.remove(str(competitor_inn))
            result["relevance"] = item_name.relevance(result["name"])
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
                    competitor_inn = ItemDB(user_id, result["url"]).get_cp_inn()
                    result["relevance"] = item_name.relevance(result["name"])
                    last_relevance = item_con[competitor_inn]["relevance"] if item_con.get(competitor_inn) else 0
                    if result["relevance"] > MIN_RELEVANCE and result["relevance"] >= last_relevance:
                        item_con[competitor_inn] = result
                        continue
        lst_relevant[item["link"]] = item_con
    if lst_relevant:
        for item_link, connections in lst_relevant.items():
            if connections:
                for cp_inn, cp_item in connections.items():
                    ItemDB(user_id, cp_item["url"]).update()
                    RelationsDB(user_id, item_link).create_relation(cp_inn=cp_inn, related_item_url=cp_item["url"])
    return redirect("/profile")
