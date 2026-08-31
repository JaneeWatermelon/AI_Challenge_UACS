"""
@file agent/actions/workspace/create.py
"""

from typing import Dict, Any, List, override
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
            "create file or directory, arguments:\n"
            "path - workspace-relative path to create (required)\n"
            "content - list of lines to write (default is empty)\n"
            "if path ends with '/', it's treated as a directory",
            arguments,
            False
        )
        self.fs = fs_service
        self.creation_cache: Path | None = None

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        self.creation_cache = Path()

        path = self.arguments.get("path")
        content = self.arguments.get("content", [])

        if path is None:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed required argument 'path'"
            )

        path_obj = Path(path)
        if str(path).endswith("/"):
            self.fs.create_directory(path_obj)
        else:
            # creates an empty file
            self.fs.create_file(path_obj, content)

        self.creation_cache = path_obj

        return ActionVerdict(
            ExitCode.SUCCESS,
            "file / directory created successfully",
            {
                "created": self.creation_cache
            }
        )

    @override
    @safe_verdict
    def reverse(self) -> ActionVerdict:
        self.fs.remove(self.creation_cache)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "created file / directory removed successfully",
            {
                "removed": self.creation_cache
            }
        )

