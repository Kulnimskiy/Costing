import os
import logging
from typing import Union
from project.helpers import hash_inn, unhash_inn


def read_file(path: str) -> Union[str, None]:
    """ Get the text from the file on its path as a string """
    try:
        text = ""
        with open(path, "r", encoding="UTF-8") as file:
            for line in file.readlines():
                text = text + line
        return text
    except FileNotFoundError:
        logging.warning(f"ERROR: FILE {path} NOT FOUND")
        return None


def create_client_folder(user_inn: str) -> bool:
    """ When the client first registers, their folder is created to store their scrapers """
    dir_name = str(user_inn)
    parent_path = ".\project\clients_scrapers"
    path = os.path.join(parent_path, dir_name)
    try:
        os.mkdir(path)
        return True
    except FileExistsError as error:
        logging.warning(f"CLIENTS FOLDER {user_inn} NOT CREATED. ERROR:{error}")
        return False


def get_cls_template(new_cls_name: str, comp_inn: Union[str, int]) -> Union[str, None]:
    """ Returns a new class tempate as a string text that can be writen to a new scraper """
    template = read_file(".\project\class_template.txt")
    if template:
        new_cls = template.replace("CLASS_NAME", new_cls_name)
        new_cls = new_cls.replace("COMPANY_INN", str(comp_inn))
        return new_cls
    return None


def create_scraper_file(user_inn: str, comp_inn: str) -> Union[str, None]:
    """ Returns the path where the scraper has been created"""
    try:
        class_name = hash_inn(comp_inn)
        user_inn = str(user_inn)
        path = f""".\project\clients_scrapers\{user_inn}\{str(comp_inn)}.py"""
        new_cls = get_cls_template(class_name, comp_inn=comp_inn)
        if new_cls:
            with open(path, "a") as file:
                file.write(new_cls)
            return path
    except FileNotFoundError as error:
        logging.warning(f"SCRAPER WASN'T CREATED FOR {user_inn} AS {error}")
        return None


def delete_empty_scraper(path: str, comp_inn: Union[str, int]) -> bool:
    """ Deletes a scraper only if it's never been changed """
    class_name = hash_inn(comp_inn)
    template = get_cls_template(class_name, comp_inn)
    scraper = read_file(path)
    if template == scraper:
        try:
            os.remove(path)
            logging.warning(f"FILE {path} WAS SUCCESSFULLY DELETED")
            return True
        except Exception as error:
            logging.warning(f"ERROR: {error}\n FILE {path} WASN'T DELETED")
            return False
    logging.warning(f"FILE {path} WASN'T DELETED AS IT HAS BEEN CHANGED")
    return False


if __name__ == "__main__":
    # create_client_folder("test")
    create_scraper_file("test", "123456789101", "123456789")
    print(hash_inn("2345"))
    print(unhash_inn(hash_inn("2345")))
