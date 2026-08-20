"""
@file agent/actions/workspace/modify/py
"""

from typing import Dict, Any, override

from ..base import Action
from ..verdict import ActionVerdict, ExitCode
from ...utils.paths import FsService


class ActionModify(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService):
        super().__init__(
            "modify",
            "midify a file line(s), arguments:\n"
            "filename - name of a file to modify\n"
            "base - index of line to insert a new line / list of lines\n"
            "replace - bool flag of the replace option\n"
            "content - inserted / replaced line(s)",
            arguments
        )
        self.fs = fs_service


    @property
    def is_replace(self) -> bool:
        return self.arguments.get("replace", False)


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }


    @override
    def execute(self) -> ActionVerdict:
        pass
