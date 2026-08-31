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


#TODO: add 'content' argument

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
        self.creation_cache = []

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        self.creation_cache = []
        paths = self.arguments.get("paths")

        if paths is None:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed required argument 'paths'"
            )

        for path in paths: 
            if path.endswith("/"):
                self.fs.create_directory(Path(path.lstrip("/")))
            else:
                # creates an empty file
                self.fs.create_file(Path(path.lstrip("/")), [""])

            self.creation_cache.append(path)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "files/directories created successfully",
            {
                "created": self.creation_cache
            }
        )

    @override
    @safe_verdict
    def reverse(self) -> ActionVerdict:
        removed = []

        for path in self.creation_cache:
            self.fs.remove(Path(path))

        return ActionVerdict(
            ExitCode.SUCCESS,
            "all created files/directories removed successfully",
            {
                "removed": removed
            }
        )

