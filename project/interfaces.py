from abc import ABCMeta, abstractmethod, abstractproperty
from typing import Union


class Manager(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def check(inpt: str) -> Union[str, None]:
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
