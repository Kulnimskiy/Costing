from project.models import Competitors, Scrapers
from project.db_manager import db_get_competitors
from project.helpers import get_cls_from_module
from app import create_app
from time import perf_counter
import importlib.util
import sys



if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        start = perf_counter()
        # test ur code here


        stop = perf_counter()
        print(stop - start)
