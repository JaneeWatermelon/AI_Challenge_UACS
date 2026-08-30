"""
@file agent/actions/workspace/file_info.py
"""

from pathlib import Path
from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService
from actions.register import ActionRegister


@ActionRegister.register("file_info")
class ActionFileInfo(Action):
    """
    Action to retrieve metadata about a file or directory.

    Provides detailed information including name, path, type,
    size, modification time, and Unix permissions.
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        """
        Initialize the file info action.

        :param arguments:   Dictionary containing the 'path' key.
        :param fs_service:  Filesystem service for metadata retrieval.
        """
        super().__init__(
            ActionFileInfo._registered_name,
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
        Execute the file info retrieval.

        Fetches metadata for the specified path and returns it
        as a structured dictionary within the verdict.

        :return:    Verdict containing the file metadata.
        """
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

    @override
    def reverse(self) -> ActionVerdict:
        """
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self.execute()
