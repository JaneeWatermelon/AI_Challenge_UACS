"""
@file agent/actions/base.py
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from .verdict import ActionVerdict


class Action(ABC):

    def __init__(self,
                 name: str,
                 description: str,
                 arguments: Dict[str, Any]):
        self.name = name
        self.description = description
        self.arguments = arguments


    @abstractmethod
    def to_json(self) -> Dict[str, Any]:
        pass


    @abstractmethod
    def execute(self) -> ActionVerdict:
        pass
