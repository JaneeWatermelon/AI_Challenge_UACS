"""
@file agent/actions/workspace/exists.py
"""

import os.path
import pathlib
from typing import Dict, Any, Optional, override

from ..base import Action
from ..verdict import ActionVerdict, ExitCode


class ActionExists(Action):

    def __init__(self, arguments: Dict[str, Any]):
        super().__init__(
            "exists",
            "checks the existing of a file or directory with arguments:\n"
            "path - relative path to the file or directory",
            arguments)


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

        is_valid, reason, path_obj = self._validate(path)
        if not is_valid:
            return ActionVerdict(
                ExitCode.INVALID_ARGUMENT,
                reason
            )

        exists = os.path.exists(path_obj)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "",
            {"exists": exists}
        )


    @staticmethod
    def _validate(path: str) -> tuple[bool, str, Optional[pathlib.Path]]:
        if len(path) > 4096:
            return False, "too long path", None

        try:
            path_obj = pathlib.Path(path)
        except ValueError as e:
            return False, f"invalid path: {str(e)}", None

        if path_obj.is_absolute():
            return False, "absolute navigation is forbidden", None

        if not ActionExists._is_path_allowed(path_obj):
            return False, "this path is not allowed in the environment", None

        return True, "ok", path_obj


    @staticmethod
    def _is_path_allowed(path_obj: pathlib.Path) -> bool:
        #TODO: environment checking
        ...
