"""
@file agent/actions/workspace/read.py
"""

from pathlib import Path
from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService


class ActionRead(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        super().__init__(
            "read",
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
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
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
        read only action (too obviously, lol)
        """
        return self
