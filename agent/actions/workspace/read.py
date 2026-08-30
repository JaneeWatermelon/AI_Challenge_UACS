"""
@file agent/actions/workspace/read.py
"""

from pathlib import Path
from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService
from actions.register import ActionRegister


@ActionRegister.register("read")
class ActionRead(Action):
    """
    Action to read a range of lines from a file.

    This is a read-only action that retrieves a specified range of lines
    from a given file and returns them as part of the verdict.
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        """
        Initialize the read action.

        :param arguments:   Dictionary containing 'filename', 'base', and 'offset'.
        :param fs_service:  Filesystem service for file operations.
        """
        super().__init__(
            ActionRead._registered_name,
            "reads a range of lines by base and offset, arguments:\n"
            "filename - name of a file to read\n"
            "base - start index of a range to read from\n"
            "offset - amount of lines to read",
            arguments,
            True
        )
        self.fs = fs_service

    @override
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize the action to a JSON-compatible dictionary.

        :return:    Dictionary representation of the action.
        """
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        """
        Execute the read operation.

        Retrieves the specified range of lines from the file
        and returns them as the verdict result.

        :return:    Verdict containing the read lines as a list.
        """
        path = self.arguments.get("filename", "")

        if not path:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'filename' argument"
            )

        full_path = self.fs.resolve_path(Path(path))

        base = self.arguments.get("base")
        offset = self.arguments.get("offset")
        content = self.fs.readlines(full_path, base, offset)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "ok",
            {"content": content}
        )

    @override
    def reverse(self) -> "ActionRead":
        """
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self
