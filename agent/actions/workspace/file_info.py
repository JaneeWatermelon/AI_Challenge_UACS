"""
@file agent/actions/workspace/file_info.py
"""

from typing import Dict, Any, override
from pathlib import Path

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService
from ...utils.assertion import safe_verdict


class ActionFileInfo(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService):
        super().__init__(
            "file_info",
            "returns metadata about a file or directory:\n"
            "- name: file/dir name\n"
            "- path: absolute path\n"
            "- is_file: true if file\n"
            "- is_dir: true if directory\n"
            "- size: size in bytes\n"
            "- modified: last modification timestamp\n"
            "- permissions: unix permissions (e.g. 755)\n"
            "arguments:\n"
            "path - path to the file or directory (relative to workspace root)",
            arguments
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
        path = self.arguments.get("path", "")

        if not path:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'path' argument"
            )

        stat = self.fs.get_metadata(Path(path))

        return ActionVerdict(
            ExitCode.SUCCESS,
            "verbose statistics",
            stat
        )
