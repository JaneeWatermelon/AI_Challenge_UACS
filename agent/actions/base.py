"""
@file agent/actions/base.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from actions.verdict import ActionVerdict


class ActionRegister:
    """
    реестр зарегестрированных действий
    представляет систему команд агента
    """

    _register: Dict[str, type['Action']] = {}


    @staticmethod
    def add_action(name: str, action_type: type['Action']) -> None:
        """
        регистрация действия
        :param name:        имя действия
        :param action_type: класс действия
        :return:            ничего
        """
        ActionRegister._register[name] = action_type


    @staticmethod
    def get_action(name: str) -> Optional[type['Action']]:
        """
        поиск действия по имени
        :param name:    имя действия
        :return:        класс действия
        """
        return ActionRegister._register.get(name)

class Action(ABC):
    """
    Базовый класс для всех действий
    минимальная единица выполнения агента
    """

    def __init__(self,
                 name: str,
                 description: str,
                 arguments: Dict[str, Any],
                 readonly: bool):
        """
        инициализация себя
        :param name:        имя действия (общее для всех представителей)
        :param description: короткое описание параметров и действия
                            (используется при генерации системного промпта)
        :param arguments:   аргументы для выполнения
        :param readonly:    True - если не может изменить файл, False - если может
        """
        self.register(name)
        self.name = name
        self.readonly = readonly
        self.description = description
        self.arguments = arguments


    @classmethod
    def register(cls, name: str):
        """
        регистрация класса для отображения по имени
        :param name:    имя действия
        :return:        ничего
        """
        if ActionRegister.get_action(name) is None:
            ActionRegister.add_action(name, cls)


    @classmethod
    def from_arguments(cls, arguments: Dict[str, Any]):
        """
        альтернативный конструкток, который должны
        поддерживать все действия (контракт)
        :param arguments:   необходимые аргементы
        :return:            объект действия
        """
        return cls(arguments)


    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """
        конвертация в джос
        :return: словарь-представление
        """
        pass


    @abstractmethod
    def execute(self) -> ActionVerdict:
        """
        непосредственно вызов команды
        :return:    результат действия
        """
        pass


    @abstractmethod
    def reverse(self):
        """
        выполнение обратного действия
        ридонли действия являются обратными к себе
        применятеся для отката
        :return:    результат обратного действия
        """
        pass
    