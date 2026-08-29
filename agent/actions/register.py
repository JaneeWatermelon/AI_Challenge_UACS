"""
@file agent/actions/register.py
"""

from typing import Dict, Optional, List, Tuple

from actions.base import Action


class ActionRegister:
    """
    Registry of registered actions.

    Represents the agent's command system.
    Maintains a mapping from action names to their corresponding classes.
    """

    _register: Dict[str, type[Action]] = {}

    @staticmethod
    def register(name: Optional[str] = None):
        """
        register action class
        :param name: registry key, uses class name if not provided
        """

        def decorator(cls):
            key = name or cls.__name__
            # name for using in action init
            cls._registered_name = key
            ActionRegister._register[key] = cls
            return cls

        return decorator

    @staticmethod
    def get_all_actions() -> List[Tuple[str, type[Action]]]:
        """
        Get all registered actions as a list of (name, class) tuples.
        :return:    List of all registered actions.
        """
        return list(ActionRegister._register.items())

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
