"""
@file agent/actions/workspace/grep.py
"""

from pathlib import Path
from typing import Dict, Any, override, Pattern

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService
from ...utils.regex import RegexService
from ...utils.assertion import safe_verdict


class ActionGrep(Action):

    def __init__(self,
                arguments: Dict[str, Any],
                fs_service: FsService=FsService(),
                regex_service: RegexService=RegexService()):
        super().__init__(
            "grep",
            "searches for a pattern in files, arguments:\n"
            "pattern - text or regex to search for (required)\n"
            "path - file or directory to search (default: workspace root)\n"
            "recursive - include subdirectories, default: false\n"
            "regex - treat pattern as regular expression, default: false\n"
            "case_sensitive - default: false\n"
            "whole_word - match whole words only, default: false\n"
            "max_results - max matches returned, default: 100\n"
            "returns: list of matches with file path, line number, and content",
            arguments,
            True
        )
        self.fs = fs_service
        self.regex = regex_service


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


    def _search_file(
            self,
            path: Path,
            pattern: Pattern[str],
            max_results: int
    ) -> list[Dict[str, Any]]:
        result = []

        lines = self.fs.readlines(path, 0, -1)

        for number, line in enumerate(lines, 1):
            match = self.regex.search(pattern, line)

            if match is None:
                continue

            result.append({
                "path": str(path),
                "line": number,
                "content": line.rstrip("\n"),
            })

            if len(result) >= max_results:
                break

        return result


    def _get_files(self, path: Path, recursive: bool) -> list[Path]:

        if path.is_file():
            return [path]

        depth = 1 if not recursive else 2**31 - 1

        return [
            item
            for item in self.fs.listdir(path, depth)
            if item.is_file()
        ]


    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        pattern_text = self.arguments.get("pattern")

        if not pattern_text:
            return ActionVerdict(
                ExitCode.INVALID_ARGUMENT,
                "missing required argument: pattern"
            )

        path = Path(self.arguments.get("path", "."))

        regex = self.regex.compile(
            pattern_text,
            regex=self.arguments.get("regex", False),
            case_sensitive=self.arguments.get("case_sensitive", False),
            whole_word=self.arguments.get("whole_word", False),
        )

        recursive = self.arguments.get("recursive", False)
        max_results = self.arguments.get("max_results", 100)

        files = self._get_files(path, recursive)

        result = []

        for file in files:
            result.extend(
                self._search_file(
                    file,
                    regex,
                    max_results - len(result)
                )
            )

            if len(result) >= max_results:
                break

        return ActionVerdict(
            ExitCode.SUCCESS,
            "grep completed",
            {"found": result}
        )


    @override
    def reverse(self) -> "ActionGrep":
        """
        read only action
        """
        return self
