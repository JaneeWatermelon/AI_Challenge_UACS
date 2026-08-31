"""
@file agent/actions/workspace/grep.py
"""

from pathlib import Path
from typing import Dict, Any, override, Pattern

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService
from utils.regex import RegexService
from utils.assertion import safe_verdict
from actions.register import ActionRegister


@ActionRegister.register("grep")
class ActionGrep(Action):
    """
    Action to search for a pattern within files.

    Supports plain text and regular expression search with
    various filtering options like case sensitivity and whole-word matching.
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService(),
                 regex_service: RegexService = RegexService()):
        """
        Initialize the grep action.

        :param arguments:       Dictionary containing search parameters.
        :param fs_service:      Filesystem service for file operations.
        :param regex_service:   Regex service for pattern compilation and matching.
        """
        super().__init__(
            ActionGrep._registered_name,
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
        """
        Serialize the action to a JSON-compatible dictionary.

        :return:    Dictionary representation of the action.
        """
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
        """
        Search for a pattern within a single file.

        Iterates through each line of the file and collects matches
        up to the specified maximum.

        :param path:            Path to the file to search.
        :param pattern:         Compiled regex pattern to match against.
        :param max_results:     Maximum number of matches to return.
        :return:                List of match dictionaries containing path, line number, and content.
        """
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
        """
        Retrieve the list of files to search based on the given path.

        If the path is a file, returns a list containing just that file.
        If it is a directory, returns all files within it,
        optionally recursing into subdirectories.

        :param path:        The starting path (file or directory).
        :param recursive:   If True, include files from subdirectories.
        :return:            List of file paths to search.
        """
        if path.is_file():
            return [path]

        depth = 1 if not recursive else 2 ** 31 - 1

        return [
            item
            for item in self.fs.listdir(path, depth)
            if item.is_file()
        ]

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        """
        Execute the grep search.

        Retrieves the pattern and optional parameters from arguments,
        compiles the regex, finds matching files, and performs the search.

        :return:    Verdict containing the list of matches found.
        """
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

        files = self._get_files(path.lstrip("/"), recursive)

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
    def reverse(self) -> ActionVerdict:
        """
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self.execute()
