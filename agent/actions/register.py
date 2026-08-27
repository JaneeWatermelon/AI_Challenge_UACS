"""
@file agent/actions/register.py
"""

from typing import Dict, Optional

from actions.base import Action


class ActionRegister:
    """
    Registry of registered actions.

    Represents the agent's command system.
    Maintains a mapping from action names to their corresponding classes.
    """

    _register: Dict[str, type[Action]] = {}

    @staticmethod
    def add_action(name: str, action_type: type[Action]) -> None:
        """
        Register a new action in the registry.

        :param name:        The unique name of the action.
        :param action_type: The action class to register.
        :return:            None
        """
        ActionRegister._register[name] = action_type

    @staticmethod
    def get_action(name: str) -> Optional[type[Action]]:
        """
        Retrieve an action class by its registered name.

        :param name:    The name of the action to look up.
        :return:        The action class if found, otherwise None.
        """
        return ActionRegister._register.get(name)
