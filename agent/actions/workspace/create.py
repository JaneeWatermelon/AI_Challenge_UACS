"""
@file agent/actions/workspace/create.py
"""

from typing import Dict, Any, override
from pathlib import Path

from actions.base import Action, ActionVerdict
from actions.verdict import ExitCode
from actions.register import ActionRegister
from utils.assertion import safe_verdict
from utils.paths import FsService


@ActionRegister.register("create")
class ActionCreate(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service=FsService()):
        super().__init__(
            ActionCreate._registered_name,
            "create files or directories, arguments:\n"
            "paths - list of paths to create (required)\n"
            "if path ends with '/', it's treated as a directory",
            arguments,
            False
        )
        self.fs = fs_service

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        paths = self.arguments.get("paths")

        if paths is None:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed required argument 'paths'"
            )

        created = []

        for path in paths:
            if path.endswith("/"):
                self.fs.create_directory(Path(path))
            else:
                # creates an empty file
                self.fs.create_file(Path(path), [""])

            created.append(path)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "files/directories created successfully",
            {
                "created": created
            }
        )

    @override
    @safe_verdict
    def reverse(self):
        pass