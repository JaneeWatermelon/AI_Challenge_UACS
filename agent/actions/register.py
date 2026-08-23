"""
@file agent/actions/register.py
"""

from typing import Dict, Optional

from AI_Challenge_UACS.agent.actions.base import Action


class ActionRegister:
    """

    """

    _register: Dict[str, type[Action]] = {}


    @staticmethod
    def add_action(name: str, action_type: type[Action]) -> None:
        ActionRegister._register[name] = action_type


    @staticmethod
    def get_action(name: str) -> Optional[type[Action]]:
        return ActionRegister._register.get(name)
