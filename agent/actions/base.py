"""
@file agent/actions/base.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from actions.verdict import ActionVerdict


class ActionRegister:
    """
    Registry of registered actions.

    Represents the agent's command system.
    Maintains a mapping from action names to their corresponding classes.
    """

    _register: Dict[str, type['Action']] = {}

    @staticmethod
    def add_action(name: str, action_type: type['Action']) -> None:
        """
        Register a new action in the registry.

        :param name:        The unique name of the action.
        :param action_type: The action class to register.
        :return:            None
        """
        ActionRegister._register[name] = action_type

    @staticmethod
    def get_action(name: str) -> Optional[type['Action']]:
        """
        Retrieve an action class by its registered name.

        :param name:    The name of the action to look up.
        :return:        The action class if found, otherwise None.
        """
        return ActionRegister._register.get(name)

class Action(ABC):
    """
    Base class for all actions.
    Represents the minimal unit of agent execution.
    """

    def __init__(self,
                 name: str,
                 description: str,
                 arguments: Dict[str, Any],
                 readonly: bool):
        """
        Initialize the action instance.

        :param name:        Unique action name (shared across all instances of this class).
        :param description: Human-readable description of the action and its parameters.
                            Used for system prompt generation.
        :param arguments:   Dictionary of arguments required for execution.
        :param readonly:    If True, the action does not modify files; if False, it may.
        """
        self.register(name)
        self.name = name
        self.readonly = readonly
        self.description = description
        self.arguments = arguments

    @classmethod
    def register(cls, name: str):
        """
        Register the action class in the global registry.

        This allows the action to be referenced by name later.
        Does nothing if the action is already registered.

        :param name:    Action name to register.
        :return:        None
        """
        if ActionRegister.get_action(name) is None:
            ActionRegister.add_action(name, cls)

    @classmethod
    def from_arguments(cls, arguments: Dict[str, Any]):
        """
        Alternative constructor that all actions must support.

        This is a contract method for creating an action instance
        from a dictionary of arguments.

        :param arguments:   Dictionary of required arguments.
        :return:            An instance of the action.
        """
        return cls(arguments)

    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize the action to a JSON-compatible dictionary.

        Used for logging, persistence, or inter-process communication.

        :return:    Dictionary representation of the action.
        """
        pass

    @abstractmethod
    def execute(self) -> ActionVerdict:
        """
        Execute the action's primary logic.

        This is the main method that performs the actual work.

        :return:    The result of the action execution.
        """
        pass

    @abstractmethod
    def reverse(self):
        """
        Perform the reverse operation for rollback.

        Read-only actions are their own reverse.
        Used to undo changes made by this action.

        :return:    The result of the reverse action.
        """
        pass
