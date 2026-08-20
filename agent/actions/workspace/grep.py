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
            "",
            arguments
        )
        self.fs = fs_service


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        pass
