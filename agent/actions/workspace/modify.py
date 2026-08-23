"""
@file agent/actions/workspace/modify/py
"""

from dataclasses import dataclass
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


@dataclass
class ModifyContext:
    old_text: List[str]
    modified_at: int
    line_count: int
    last_modified_path: Path


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
        self.context = ModifyContext([], -1, 0, Path())


    @property
    def mode(self) -> ModifyOption:
        mode_map = {
            ModifyOption.DELETE.value: ModifyOption.DELETE,
            ModifyOption.INSERT.value: ModifyOption.INSERT,
            ModifyOption.APPEND.value: ModifyOption.APPEND,
        }
        return mode_map.get(self.arguments.get("mode"), ModifyOption.REPLACE)


    def update_context(self,
                       *,
                       old_text: List[str] | None,
                       modified_at: int | None,
                       linecount: int | None,
                       last_modified_file: Path | None
            ) -> None:
        if old_text:
            self.context.old_text = old_text
        if modified_at:
            self.context.modified_at = modified_at
        if last_modified_file:
            self.context.last_modified_path = last_modified_file
        if linecount:
            self.context.line_count = linecount


    def _replace(self,
                 path: Path,
                 base: int,
                 offset: int,
                 content: List[str]
            ) -> ActionVerdict:
        self.update_context(
            old_text=self.fs.readlines(path, base, offset),
            modified_at=base,
            last_modified_file=path
        )
        self.fs.replacelines(path, base, offset, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.REPLACE}"
        )


    def _cancel_replace(self) -> ActionVerdict:
        return self._replace(
            self.context.last_modified_path,
            self.context.modified_at,
            self.context.line_count,
            self.context.old_text
        )


    def _delete(self,
                path: Path,
                base: int,
                offset: int
            ) -> ActionVerdict:
        self.update_context(
            old_text=self.fs.readlines(path, base, offset),
            modified_at=base,
            last_modified_file=path
        )
        return self._replace(path, base, offset, [""])


    def _cancel_delete(self) -> ActionVerdict:
        return self._insert(
            self.context.last_modified_path,
            self.context.modified_at,
            self.context.old_text
        )


    def _append(self,
                path: Path,
                content: List[str]
            ) -> ActionVerdict:
        self.update_context(
            modified_at=self.fs.linecount(path),
            last_modified_file=path,
            linecount=len(content)
        )
        self.fs.appendlines(path, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.APPEND}"
        )


    def _cancel_append(self) -> ActionVerdict:
        return self._delete(
            self.context.last_modified_path,
            self.context.modified_at,
            self.context.line_count
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


    def _cancel_insert(self) -> ActionVerdict:
        return self._delete(
            self.context.last_modified_path,
            self.context.modified_at,
            self.context.line_count
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


    @override
    def reverse(self) -> ActionVerdict:
        mode_map = {
            ModifyOption.DELETE: ActionModify._cancel_delete,
            ModifyOption.INSERT: ActionModify._cancel_insert,
            ModifyOption.APPEND: ActionModify._cancel_append,
            ModifyOption.REPLACE: ActionModify._cancel_replace
        }
        canceler = mode_map[self.mode]
        return canceler()
