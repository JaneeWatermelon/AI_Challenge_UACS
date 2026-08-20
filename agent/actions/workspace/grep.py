"""
@file agent/actions/workspace/grep.py
"""

from typing import Dict, Any, override

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService
from ...utils.assertion import safe_verdict


class ActionGrep(Action):

    def __init__(self, arguments: Dict[str, Any], fs_service: FsService):
        super().__init__(
            "grep",
            "searches for a pattern in files, arguments:\n"
            "pattern - text or regex to search for (required)\n"
            "path - file or directory to search (default: workspace root)\n"
            "recursive - include subdirectories, default: false\n"
            "case_sensitive - default: false\n"
            "whole_word - match whole words only, default: false\n"
            "max_results - max matches returned, default: 100\n"
            "returns: list of matches with file path, line number, and content",
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
        pass
