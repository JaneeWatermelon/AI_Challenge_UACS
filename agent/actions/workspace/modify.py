"""
@file agent/actions/workspace/modify/py
"""

from typing import Dict, Any, List, override
from pathlib import Path
from enum import Enum

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService
from ...utils.assertion import safe_verdict


class ModifyOption(Enum):
    REPLACE="replace"
    APPEND="append"
    DELETE="delete"
    INSERT="insert"

    def __str__(self):
        return self.value


class ActionModify(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService=FsService()):
        super().__init__(
            "modify",
            "midify a file line(s), arguments:\n"
            "filename - name of a file to modify\n"
            "base - index of line to insert a new lines\n"
            f"offset - used with {ModifyOption.REPLACE} or {ModifyOption.DELETE}"
            "mode - mode of modification: "
            f"{ModifyOption.APPEND}, {ModifyOption.APPEND},"
            f"{ModifyOption.DELETE}, {ModifyOption.INSERT}\n"
            "content - list of lines\n"
            "p.s.\n"
            "base is not required with append mode\n"
            f"default option is {ModifyOption.DELETE}",
            arguments,
            False
        )
        self.fs = fs_service


    @property
    def mode(self) -> ModifyOption:
        mode_map = {
            ModifyOption.DELETE.value: ModifyOption.DELETE,
            ModifyOption.INSERT.value: ModifyOption.INSERT,
            ModifyOption.APPEND.value: ModifyOption.APPEND,
        }
        return mode_map.get(self.arguments.get("mode"), ModifyOption.REPLACE)


    def _replace(self,
                 path: Path,
                 base: int,
                 offset: int,
                 content: List[str]
            ) -> ActionVerdict:
        self.fs.replacelines(path, base, offset, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.REPLACE}"
        )


    def _delete(self,
                path: Path,
                base: int,
                offset: int
            ) -> ActionVerdict:
        return self._replace(path, base, offset, [""])


    def _append(self,
                path: Path,
                content: List[str]
            ) -> ActionVerdict:
        self.fs.appendlines(path, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.APPEND}"
        )


    def _insert(self,
                path: Path,
                base: int,
                content: List[str]
            ) -> ActionVerdict:
        self.fs.insertlines(path, base, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.INSERT}"
        )


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
        filename = self.arguments.get("filename", "")
        mode = self.arguments.get("mode", "")

        if not filename or not mode:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'filename' or 'mode' argument"
            )

        full_path = self.fs.resolve_path(Path(filename))

        mode = self.mode
        base = self.arguments.get("base")
        offset = self.arguments.get("offset")
        content = self.arguments.get("content")

        if mode == ModifyOption.DELETE:
            return self._delete(full_path, base, offset)

        elif mode == ModifyOption.APPEND:
            return self._append(full_path, content)

        elif mode == ModifyOption.REPLACE:
            return self._replace(full_path, base, offset, content)

        else:
            return self._insert(full_path, base, content)
