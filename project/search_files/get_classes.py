import sys
import inspect
import importlib.util
from project.models import Competitors, Scrapers


def db_get_competitor(user_id, com_inn):
    return Competitors.query.filter_by(user_id=user_id, competitor_inn=com_inn).first()


def db_get_competitors(user_id, connection_status=""):
    """connection status can be 'disconnected', 'connected','requested'. Only those are in the db"""
    if connection_status:
        return Competitors.query.filter_by(user_id=user_id, connection_status=connection_status).all()
    return Competitors.query.filter_by(user_id=user_id).all()


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


def get_scr_from_id(user_id, comp_inn=None, path=False):
    """ If competitor's inn is not provided, it returns a list of all the scrapers connected
    to the user by their id. Else it returns a scraper for a specific competitor"""
    if comp_inn:
        competitor = db_get_competitor(user_id, comp_inn)
        if competitor:
            scr_path = Scrapers.query.filter_by(company_inn=comp_inn).first().scraper_path
            if path:
                return scr_path
            if competitor.connection_status == "connected":
                cls = get_cls_from_path(scr_path)[0]
                return cls
            else:
                print(f"The competitor {comp_inn} is not connected")
                return None
    competitors_ = db_get_competitors(user_id, "connected")
    inns_ = [competitor.competitor_inn for competitor in competitors_]
    scr_path = Scrapers.query.filter(Scrapers.company_inn.in_(inns_)).all()
    classes = [get_cls_from_path(scr.scraper_path)[0] for scr in scr_path]
    return classes


def get_cls_from_module(module_name):
    """get all the cls instances within a python file without the imported ones
    use module_name=sys.modules[__name__] to get classes form your file"""

    cls_members = inspect.getmembers(module_name, inspect.isclass)  # get ALL the classes (class_name, class_object)
    # remove the imported classes
    cls_objects = [obj for name, obj in cls_members if obj.__dict__.get("BASE_URL", None)]
    return cls_objects
