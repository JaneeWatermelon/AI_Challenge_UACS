"""
@file agent/actions/workspace/ignore.py
"""

from typing import Dict, Any, override

from ..base import Action
from ..verdict import ActionVerdict, ExitCode


class ActionIgnore(Action):

    def __init__(self, arguments: Dict[str, Any]):
        super().__init__(
            "ignore",
            "ignoring a reply",
            arguments,
            True
        )


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


    @override
    def execute(self) -> ActionVerdict:
        return ActionVerdict(
            ExitCode.SUCCESS,
            "ignored"
        )


    @override
    def reverse(self) -> "ActionFileInfo":
        """
        already reversed
        """
        return self
