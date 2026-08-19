"""
@file agent/actions/workspace/file_info.py
"""

from typing import Dict, Any

from ..base import Action
from ..verdict import ActionVerdict


class ActionFileInfo(Action):

    def __init__(self, arguments: Dict[str, Any]):
        super().__init__(
            "file_info",
            "researches verbose info about a file with arguments:\n"
            "file_path - path to the allowed file\n"
            "fields - comma-separated field names (last_modified, size, flags, nlink)\n"
            "fields=last_modified,size,flags e.g.",
            arguments
        )


    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }


    def execute(self) -> ActionVerdict:
        pass
