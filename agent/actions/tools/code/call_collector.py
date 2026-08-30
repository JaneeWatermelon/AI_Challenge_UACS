"""
@file agent/actions/code/call_collector.py
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from models.record import Record
from utils.assertion import safe_verdict
from utils.paths import FsService
from utils.regex import RegexService
from utils.assertion import safe_verdict
from actions.register import ActionRegister


_CALL_PATTERN = re.compile(
    r"(?<![\w.])(?:[A-Za-z_][A-Za-z0-9_]*\.)*([A-Za-z_][A-Za-z0-9_]*)\s*\("
)


@ActionRegister.register("call_collector")
class ActionCallCollector(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        super().__init__(
            ActionCallCollector._registered_name,
            "collects function/method calls from source files, arguments:\n"
            "files - list of file paths to analyze (required)\n"
            "name - optional: specific function name to find (default: all)\n"
            "returns: mapping file_path -> list of calls found",
            arguments,
            True
        )
        self.fs = fs_service

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }

    @staticmethod
    def _collect_from_text(filename: str, text: str, name_matcher: Optional[re.Pattern]) -> List[Record]:
        records: List[Record] = []

        for lineno, line in enumerate(text.splitlines(), start=1):
            found_on_line: List[str] = []

            for match in _CALL_PATTERN.finditer(line):
                call_name = match.group(1)

                if name_matcher is not None and not name_matcher.search(call_name):
                    continue

                found_on_line.append(call_name)

            if found_on_line:
                records.append(Record(filename=filename, base=lineno, content=found_on_line))

        return records

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        files = self.arguments.get("files")

        if not files:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'files' argument"
            )

        target_name = self.arguments.get("name")
        name_matcher = (
            RegexService.compile(target_name, regex=False, whole_word=True)
            if target_name else None
        )

        result: List[Record] = []

        for raw_path in files:
            path = Path(raw_path)

            self.fs._path_assert(path)

            full_path = self.fs.resolve_path(path)
            text = full_path.read_text(encoding="utf-8", errors="replace")

            result.extend(self._collect_from_text(str(path), text, name_matcher))

        return ActionVerdict(
            ExitCode.SUCCESS,
            "function calls collected",
            {"found": result}
        )

    @override
    @safe_verdict
    def reverse(self) -> "ActionCallCollector":
        """
        read only action
        """
        return self
