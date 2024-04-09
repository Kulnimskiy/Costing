import os
import sys
import logging
import inspect
import importlib.util
from typing import Union
from project.wreckage.helpers import hash_inn

FOLDERS_PATH = "./project/clients_scrapers"
SCRAPER_TEMPLATE_PATH = "./project/text_templates/class_template.txt"


class FileSystem:
    """ Used to systemize files in the project
        Provide the full path to the file you want to use this class on"""

    def __init__(self, path: str):
        self.path = path

    def read(self) -> Union[str, None]:
        """ Get the text from the file on its path as a string """
        try:
            text = ""
            with open(self.path, "r", encoding="UTF-8") as file:
                for line in file.readlines():
                    text = text + line
            return text
        except FileNotFoundError:
            logging.warning(f"ERROR: FILE {self.path} NOT FOUND")
            return None

    def create(self, file_text: str = ""):
        """ Creates file by the provided path. Returns file path if it was created successfully """
        try:
            with open(self.path, "a") as file:
                file.write(file_text)
                logging.warning(f"FILE {self.path} HAS BEEN CREATED")
            return self.path
        except FileNotFoundError as error:
            logging.warning(f"ERROR: CANNOT CREATE FILE {self.path} \n{error}")
            return None

    def delete(self) -> bool:
        try:
            if os.path.isfile(self.path):
                os.remove(self.path)
                logging.warning(f"FILE {self.path} WAS SUCCESSFULLY DELETED")
                return True
            return False
        except Exception as error:
            logging.warning(f"ERROR: FILE {self.path} WASN'T DELETED \n{error}")
            return False


class FolderSystem:
    """Used to systemize folders in the project"""

    def __init__(self, dir_name: str):
        self.dir_name = dir_name
        self.path = os.path.join(FOLDERS_PATH, dir_name)

    def create(self):
        try:
            os.mkdir(self.path)
            return self.path
        except FileExistsError as error:
            logging.warning(f"ERROR: CLIENTS FOLDER {self.path} NOT CREATED \n{error}")
            return False

    def delete(self):
        """ Deletes empty dirs"""
        try:
            if os.path.isdir(self.path):
                os.rmdir(self.path)
                return True
            return False
        except FileExistsError as error:
            logging.warning(f"ERROR: FOLDER {self.path} NOT DELETED \n{error}")
            return False


class ScraperSystem:
    """ Used to work with Scraper files """
    def __init__(self, user_inn: str, cp_inn):
        self.user_inn = user_inn
        self.cp_inn = cp_inn

    def get_template(self, new_cls_name: str) -> Union[str, None]:
        """ Returns a new class template as a string text that can be writen to a new scraper """
        template = FileSystem(SCRAPER_TEMPLATE_PATH).read()
        if template:
            scraper = template.format(CLASS_NAME=new_cls_name, COMPANY_INN=self.cp_inn)
            return scraper
        return None

    @staticmethod
    def get_from_module(module_name):
        """ Gets all the scrapers from a chosen module.
            To choose a module try module_name=sys.modules[__name__]"""
        cls_members = inspect.getmembers(module_name, inspect.isclass)  # get ALL the classes (class_name, class_object)
        cls_objects = [obj for name, obj in cls_members if obj.__dict__.get("BASE_URL", None)]  # leave only Scrapers
        return cls_objects

    @staticmethod
    def get_from_path(path):
        """first you import the module, a list of classes and del the module from the file"""
        try:
            spec = importlib.util.spec_from_file_location("scraper", path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["scraper"] = module
            spec.loader.exec_module(module)
            cls = ScraperSystem.get_from_module(module)
            sys.modules.pop('scraper')
            return cls
        except FileNotFoundError as error:
            logging.warning(f"ERROR: THE PATH '{path}' DOESN'T HAVE ANY SCRAPER \n{error}")
            return None

    def create(self) -> Union[str, None]:
        """ Returns the path where the scraper has been created"""
        folder_name = str(self.user_inn)
        file_name = self.cp_inn
        class_name = hash_inn(self.cp_inn)
        path = os.path.join(FOLDERS_PATH, folder_name, file_name + ".py")

        # path = ScraperSystem.SCRAPER_PATH.format(folder=folder_name, file=file_name)
        scraper_template = self.get_template(class_name)
        return FileSystem(path).create(scraper_template)

    def delete(self, path: str) -> bool:
        """ Deletes a scraper file only if it's never been changed """
        class_name = hash_inn(self.cp_inn)
        template = self.get_template(class_name)
        scraper_file = FileSystem(path)
        if template == scraper_file.read():
            return scraper_file.delete()
        logging.warning(f"FILE {path} WASN'T DELETED AS IT HAS BEEN CHANGED")
        return False
