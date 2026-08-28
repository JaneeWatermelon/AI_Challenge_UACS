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
    """
    Action to retrieve a directory tree structure.

    This is a read-only action that walks a specified directory
    and returns a list of endpoints (files and directories) up to
    a configurable depth.
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        """
        Initialize the tree action.

        :param arguments:   Dictionary containing 'path' and optional 'max_depth'.
        :param fs_service:  Filesystem service for directory traversal.
        """
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
        """
        Get the workspace root directory.

        :return:    Path to the workspace root.
        """
        return self.fs.workspace_dir

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
            "workspace_dir": self.workspace_dir,
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        """
        Execute the directory tree traversal.

        Walks the specified directory (or workspace root if not specified)
        and returns a list of endpoints up to the given depth.

        :return:    Verdict containing the list of endpoints.
        """
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
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self
