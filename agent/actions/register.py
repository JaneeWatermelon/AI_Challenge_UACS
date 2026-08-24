"""
@file agent/actions/register.py
"""

from typing import Dict, Optional

from agent.actions.base import Action


class ActionRegister:
    """
    реестр зарегестрированных действий
    представляет систему команд агента
    """

    _register: Dict[str, type[Action]] = {}


    @staticmethod
    def add_action(name: str, action_type: type[Action]) -> None:
        """
        регистрация действия
        :param name:        имя действия
        :param action_type: класс действия
        :return:            ничего
        """
        ActionRegister._register[name] = action_type


    @staticmethod
    def get_action(name: str) -> Optional[type[Action]]:
        """
        поиск действия по имени
        :param name:    имя действия
        :return:        класс действия
        """
        return ActionRegister._register.get(name)
