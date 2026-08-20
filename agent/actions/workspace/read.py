"""
@file agent/actions/workspace/read.py
"""

from typing import Dict, Any, List, override
from pathlib import Path

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService


class ActionRead(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService):
        super().__init__(
            "read",
            "reads a single line by index or a range by base and offset, arguments:\n"
            "filename - name of a file to read\n"
            "line - index of a single line to read\n"
            "base - start index of a range to read from\n"
            "offset - amount of lines to read",
            arguments
        )
        self.fs = fs_service


    @property
    def single(self) -> bool:
        return self.arguments.__contains__("line")


    def _readline(self, path: Path, idx: int) -> str:
        return self.fs.readline(path, idx)


    def _readlines(self, path: Path, base: int, offset: int) -> List[str]:
        return self.fs.readlines(path, base, offset)


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }


    @override
    def execute(self) -> ActionVerdict:
        path = self.arguments.get("filename", "")

        if not path:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'filename' argument"
            )

        try:
            full_path = self.fs.resolve_path(Path(path))

            if self.single:
                idx = self.arguments.get("line")
                content = self._readline(full_path, idx)

            else:
                base = self.arguments.get("base")
                offset = self.arguments.get("offset")
                content = self._readlines(full_path, base, offset)

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

        return ActionVerdict(
            ExitCode.SUCCESS,
            "ok",
            {"content": content}
        )
