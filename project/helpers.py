import sys
import decimal
import inspect
import requests
import validators
import importlib.util
from datetime import datetime
from email_validator import validate_email, EmailNotValidError


def email_checker(email):
    try:
        v = validate_email(str(email))
        email = v.__dict__["normalized"]
        return email
    except EmailNotValidError as error:
        print(error)
        return False


def password_checker(password: str):
    """The password of 6 char lengths has to have digits and alpha char of lower and upper case with no space"""
    password = str(password).strip()
    length_req = len(password) >= 6
    number_req = any(symbol.isdigit() for symbol in password)
    no_space_req = all(not symbol.isspace() for symbol in password)
    upper_req = any(symbol.isupper() for symbol in password)
    lower_req = any(symbol.islower() for symbol in password)
    # alpha_req = any(symbol.isalpha() for symbol in password)  ## you don't need this as u have the upper and lower req
    if all([no_space_req, length_req, number_req, upper_req, lower_req]):  # alpha_req is removed
        return password
    return False


def inn_checker(inn_: str):
    """for testing purposes the algorithm of checking if the inn exists is not implemented"""
    inn_ = str(inn_).strip()
    people_len = 10
    company_len = 12
    if len(inn_) != people_len and len(inn_) != company_len:
        return False
    if any(not digit.isdigit() for digit in inn_):
        return False
    return int(inn_)


def login_checker(login):
    login = str(login).strip()
    no_space_req = all(not symbol.isspace() for symbol in login)
    length_req = len(login) >= 3
    if all([login, no_space_req, length_req]):
        return login
    return False


def get_cur_date():
    return datetime.today().strftime("%d.%m.%Y")


def get_cls_from_module(module_name):
    """get all the cls instances within a python file without the imported ones
    use module_name=sys.modules[__name__] to get classes form your file"""

    cls_members = inspect.getmembers(module_name, inspect.isclass)  # get ALL the classes (class_name, class_object)
    # remove the imported classes
    cls_objects = [obj for name, obj in cls_members if obj.__dict__.get("BASE_URL", None)]
    return cls_objects


def operate(operation, info=None):
    """function to process the result from parsing"""
    try:
        if info:
            result = operation(info)
            return result
        return operation()
    except (AttributeError, TypeError, ValueError) as e:
        print(e)
        return None


def convert_to_rub(amount: (int, float), currency: str):
    """convert currencies into Russian Ruble """
    currency = currency.strip().upper()
    try:
        data = requests.get('https://www.cbr-xml-daily.ru/latest.js').json()
        currency_rate = float(data["rates"][f"{currency}"])
        return int(amount / currency_rate)
    except Exception as error:
        print(error)
        return None


def calculate_relevance(search: str, result: str):
    words = search.split()
    counter = 0
    for word in words:
        if len(word) > 5:
            word = word[1:-2]
        if word.lower() in result.lower():
            counter += 1
    return counter / len(words)


def hash_inn(comp_inn: str):
    comp_inn = str(comp_inn)
    value = ""
    for digit in comp_inn:
        value += chr(100 + int(digit))
    return value.lower().capitalize()


def unhash_inn(comp_hash: str):
    value = ""
    for letter in comp_hash:
        value += str(ord(letter.lower()) - 100)
    return value


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


def check_price(price: str):
    try:
        price = int("".join([digit for digit in price if digit.isdigit()]))
        return price
    except (TypeError, ValueError):
        return None


def format_search_all_result(item, result: dict, competitors, min_price=None, max_price=None,):

    for r in result:
        if r["price"] is None:
            r["price"] = 0
        for competitor in competitors:
            if competitor.competitor_website in r["url"]:
                r["competitor"] = competitor.competitor_nickname
    if min_price:
        result = filter(lambda x: x["price"] >= min_price, result)
    if max_price:
        result = filter(lambda x: x["price"] <= max_price, result)
    result = sorted(list(result), key=lambda r: (calculate_relevance(item, r["name"]), r["price"]), reverse=True)
    for r in result:
        if r["price"] == 0:
            r["price"] = "Not selling || Not found"
        else:
            r["price"] = decimal.Decimal(str(r["price"]))
            r["price"] = '{0:,}'.format(r["price"]).replace(',', ' ')
    return result


def get_link(link):
    if not link:
        return None
    if "http" in link and validators.url(link):
        return link
    else:
        link = "https://" + link
        if validators.url(link):
            return link
    return None


if __name__ == "__main__":
    print(get_link("dentikom/delivery-and-payment/delivery/"))
