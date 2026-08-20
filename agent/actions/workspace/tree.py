"""
@file agent/actions/workspace/tree.py
"""

from typing import Dict, Any, override
from pathlib import Path

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService


DEFAULT_DEPTH = 1


class ActionTree(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService):
        super().__init__(
            "tree",
            "returns a directory tree structure, arguments:\n"
            "path - path to directory to walk (default: workspace root)\n"
            f"max_depth - maximum recursion depth (default: {DEFAULT_DEPTH})\n"
            "returns:\n"
            "endpoints: list of endpoints",
            arguments
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
    def execute(self) -> ActionVerdict:
        path = self.arguments.get("path", "")
        depth = self.arguments.get("max_depth", DEFAULT_DEPTH)

        try:
            endpoints = self.fs.listdir(Path(path), depth)
            return ActionVerdict(
                ExitCode.SUCCESS,
                "walked",
                {"endpoints": endpoints}
            )

        except PermissionError as e:
            return ActionVerdict(
                ExitCode.PERMISSION_DENIED,
                str(e)
            )

        except ValueError as e:
            return ActionVerdict(
                ExitCode.INVALID_ARGUMENT,
                str(e)
            )

        except Exception as e:
            return ActionVerdict(
                ExitCode.EXECUTION_ERROR,
                str(e)
            )
