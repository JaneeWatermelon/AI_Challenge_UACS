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
from ...models.record import Record


class ModifyOption(Enum):
    """
    опции для модификации файла
    """

    REPLACE = "replace"
    APPEND = "append"
    DELETE = "delete"
    INSERT = "insert"

    def __str__(self):
        return self.value


class ActionModify(Action):
    """
    действие изменения файла
    """

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
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
        self.context = Record(filename="", base=-1, content=[])


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
                        filename: str | None = None,
                        base: int | None = None,
                        content: List[str] | None = None
            ) -> None:
        self.context = Record(
            filename=filename if filename is not None else self.context.filename,
            base=base if base is not None else self.context.base,
            content=content if content is not None else self.context.content,
        )


    def _replace(self,
                 path: Path,
                 base: int,
                 offset: int,
                 content: List[str]
            ) -> ActionVerdict:
        self.update_context(
            filename=str(path),
            base=base,
            content=self.fs.readlines(path, base, offset)
        )
        self.fs.replacelines(path, base, offset, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.REPLACE}"
        )


    def _cancel_replace(self) -> ActionVerdict:
        return self._replace(
            Path(self.context.filename),
            self.context.base,
            len(self.context.content),
            self.context.content
        )


    def _delete(self,
                path: Path,
                base: int,
                offset: int
            ) -> ActionVerdict:
        self.update_context(
            filename=str(path),
            base=base,
            content=self.fs.readlines(path, base, offset)
        )
        return self._replace(path, base, offset, [""])


    def _cancel_delete(self) -> ActionVerdict:
        return self._insert(
            Path(self.context.filename),
            self.context.base,
            self.context.content
        )


    def _append(self,
                path: Path,
                content: List[str]
            ) -> ActionVerdict:
        self.update_context(
            filename=str(path),
            base=self.fs.linecount(path),
            content=content
        )
        self.fs.appendlines(path, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.APPEND}"
        )


    def _cancel_append(self) -> ActionVerdict:
        return self._delete(
            Path(self.context.filename),
            self.context.base,
            len(self.context.content)
        )


    def _insert(self,
                path: Path,
                base: int,
                content: List[str]
            ) -> ActionVerdict:
        self.update_context(
            filename=str(path),
            base=base,
            content=content
        )
        self.fs.insertlines(path, base, content)
        return ActionVerdict(
            ExitCode.SUCCESS,
            f"{ModifyOption.INSERT}"
        )


    def _cancel_insert(self) -> ActionVerdict:
        return self._delete(
            Path(self.context.filename),
            self.context.base,
            len(self.context.content)
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
            ModifyOption.DELETE: self._cancel_delete,
            ModifyOption.INSERT: self._cancel_insert,
            ModifyOption.APPEND: self._cancel_append,
            ModifyOption.REPLACE: self._cancel_replace,
        }
        canceler = mode_map[self.mode]
        return canceler()
