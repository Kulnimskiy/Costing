from project.models import Competitors, Scrapers
from project.db_manager import db_get_competitors
from project.helpers import get_cls_from_module
from app import create_app
from time import perf_counter
import importlib.util
import sys


def get_cls_from_path(path):
    """first you import the module, a list of classes and del the module from the file"""
    try:
        spec = importlib.util.spec_from_file_location("scraper", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["scraper"] = module
        spec.loader.exec_module(module)
        classes = get_cls_from_module(module)
        sys.modules.pop('scraper')
        return classes
    except FileNotFoundError as e:
        print(e)
        print(f"There is no such scraper on the path: {path}")
        return None


def db_get_scr_from_id(user_id):
    """get all the scrapers connected to the user by their id"""
    competitors_ = db_get_competitors(1, "connected")
    inns_ = [competitor.competitor_inn for competitor in competitors_]
    scr_path = Scrapers.query.filter(Scrapers.company_inn.in_(inns_)).all()
    classes = [get_cls_from_path(scr.scraper_path)[0] for scr in scr_path]
    return classes


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        start = perf_counter()
        for i in db_get_scr_from_id(1):
            print(i.BASE_URL)
        stop = perf_counter()
        print(stop - start)
