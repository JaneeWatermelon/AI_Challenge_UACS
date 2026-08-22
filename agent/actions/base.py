"""
@file agent/actions/base.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from .verdict import ActionVerdict
from .register import ActionRegister


class Action(ABC):

    def __init__(self,
                 name: str,
                 description: str,
                 arguments: Dict[str, Any]):
        self.register(name)
        self.description = description
        self.arguments = arguments


    @classmethod
    def register(cls, name: str):
        ActionRegister.add_action(name, cls)


    @classmethod
    def from_arguments(cls, arguments: Dict[str, Any]):
        return cls(arguments)


    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass


    @abstractmethod
    def execute(self) -> ActionVerdict:
        pass
