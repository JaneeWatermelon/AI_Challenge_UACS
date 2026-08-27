"""
@file agent/actions/workspace/tree.py
"""

from pathlib import Path
from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService

DEFAULT_DEPTH = 1


class ActionTree(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        super().__init__(
            "tree",
            "returns a directory tree structure, arguments:\n"
            "path - path to directory to walk (default: workspace root)\n"
            f"max_depth - maximum recursion depth (default: {DEFAULT_DEPTH})\n"
            "returns:\n"
            "endpoints: list of endpoints",
            arguments,
            True
        )
        self.fs = fs_service

    @property
    def workspace_dir(self) -> Path:
        return self.fs.workspace_dir

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
            "workspace_dir": self.workspace_dir,
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        path = self.arguments.get("path", "")
        depth = self.arguments.get("max_depth", DEFAULT_DEPTH)

        endpoints = self.fs.listdir(Path(path), depth)
        return ActionVerdict(
            ExitCode.SUCCESS,
            "walked",
            {"endpoints": endpoints}
        )

    @override
    def reverse(self) -> "ActionTree":
        """
        read only action
        """
        return self
