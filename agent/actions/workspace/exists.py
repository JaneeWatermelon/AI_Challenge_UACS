"""
@file agent/actions/workspace/exists.py
"""

from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService


class ActionExists(Action):
    """
    действие проверки существования файла или директории
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        super().__init__(
            "exists",
            "checks the existing of a file or directory with arguments:\n"
            "path - relative path to the file or directory",
            arguments,
            True
        )
        self.fs = fs_service

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments:": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        path = self.arguments.get("path")

        if path is None:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                f"see the description:\n{self.description}"
            )

        is_valid, reason, path_obj = self.fs.validate_path(path)
        if not is_valid:
            return ActionVerdict(
                ExitCode.INVALID_ARGUMENT,
                reason
            )

        if not self.fs.is_path_allowed(path_obj):
            return ActionVerdict(
                ExitCode.INVALID_ARGUMENT,
                f"given path is not allowed: {str(path)}"
            )

        return ActionVerdict(
            ExitCode.SUCCESS,
            "",
            {"exists": path_obj.exists()}
        )

    @override
    def reverse(self) -> "ActionExists":
        """
        read only action
        """
        return self
