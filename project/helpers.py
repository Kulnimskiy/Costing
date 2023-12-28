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
    alpha_req = any(symbol.isalpha() for symbol in password)
    if all([no_space_req, length_req, number_req, upper_req, lower_req, alpha_req]):
        return password
    return False


def inn_checker(inn: str):
    """for testing purposes the algorithm of checking if the inn exists is not implemented"""
    inn = str(inn).strip()
    people_len = 10
    company_len = 12
    if len(inn) != people_len and len(inn) != company_len:
        return False
    if any(not digit.isdigit() for digit in inn):
        return False
    return int(inn)


if __name__ == "__main__":
    emails = ["ser@yandex.ru", "sk@agv.ag", "ag.com", "sf@yan.rewq"]
    passwords = ["12", "agv", "agv12", "  aGv123 ", "Ag v123", "agv123", "AGV123"]
    inn = [123456789101, "1234n5678101", "123456 89101", "12345678910", "1234567890"]
    for i in inn:
        print(inn_checker(i))
