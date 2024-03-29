from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Union


class Manager(metaclass=ABCMeta):

    @abstractmethod
    def check(self) -> Union[str, None]:
        pass


class Hasher(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def hash(inpt: str) -> Union[str, bool]:
        pass

    @staticmethod
    @abstractmethod
    def decode(inpt: str) -> Union[str, bool]:
        pass


class Messanger(metaclass=ABCMeta):
    @abstractmethod
    def message(self, text: str, subject: str = "Messager"):
        pass
