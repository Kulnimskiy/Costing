def password_checker(password: str):
    password = str(password).strip()
    length_req = len(password) >= 6
    number_req = False
    no_space_req = False
    for symbol in password:
        if symbol.isspace():
            break
        if symbol.isdigit():
            number_req = True
    else:
        no_space_req = True
    if all([no_space_req, length_req, number_req]):
        return password
    return False
