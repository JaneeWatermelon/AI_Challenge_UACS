"""
@file agent/actions/workspace/exists.py
"""

from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService
from actions.register import ActionRegister


@ActionRegister.register("exists")
class ActionExists(Action):
    """
    Action to check whether a file or directory exists.

    This is a read-only action that verifies the existence
    of a given path within the workspace.
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        """
        Initialize the exists action.

        :param arguments:   Dictionary containing the 'path' key.
        :param fs_service:  Filesystem service for path validation and checks.
        """
        super().__init__(
            ActionExists._registered_name,
            "checks the existing of a file or directory with arguments:\n"
            "path - relative path to the file or directory",
            arguments,
            True
        )
        self.fs = fs_service

    @classmethod
    def parameters_schema(cls) -> dict:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path to a file or directory",
                },
            },
            "required": ["path"],
            "additionalProperties": False,
        }

    @override
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize the action to a JSON-compatible dictionary.

        :return:    Dictionary representation of the action.
        """
        return {
            "name": self.name,
            "description": self.description,
            "arguments:": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        """
        Execute the existence check.

        Retrieves the 'path' argument, validates it,
        and returns a verdict indicating whether the path exists.

        :return:    Verdict containing the existence result.
        """
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
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self
