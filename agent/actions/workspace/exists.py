"""
@file agent/actions/workspace/exists.py
"""

import os.path
import pathlib
from typing import Dict, Any, override

from ..base import Action
from ..verdict import ActionVerdict, ExitCode


class ActionExists(Action):

    def __init__(self, arguments: Dict[str, Any]):
        super().__init__(
            "exists",
            "checks the existing of a file or directory with arguments:\n"
            "path - relative path to the file or directory"
            , arguments)


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments:": self.arguments
        }


    @override
    def execute(self) -> ActionVerdict:
        path = self.arguments.get("path")

        if path is None:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                f"see the description:\n{self.description}"
            )

        exists = os.path.exists(pathlib.Path(path))

        return ActionVerdict(
            ExitCode.SUCCESS,
            "",
            {"exists": exists}
        )
