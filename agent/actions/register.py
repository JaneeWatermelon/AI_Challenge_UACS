"""
@file agent/actions/register.py
"""

from typing import Dict

from AI_Challenge_UACS.agent.actions.base import Action


class ActionRegister:
    """

    """

    register: Dict[str, type[Action]] = {}

    @staticmethod
    def add_action(name: str, action_type: type[Action]) -> None:
        ActionRegister.register[name] = action_type
