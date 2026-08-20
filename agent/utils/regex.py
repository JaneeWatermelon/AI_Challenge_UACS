"""
@file agent/utils/regex.py
"""

import re
from typing import Pattern


class RegexService:

    @staticmethod
    def compile(
            pattern: str,
            regex: bool = True,
            case_sensitive: bool = False,
            whole_word: bool = False
    ) -> Pattern[str]:

        if not regex:
            pattern = re.escape(pattern)

        if whole_word:
            pattern = rf"\b(?:{pattern})\b"

        flags = 0 if case_sensitive else re.IGNORECASE

        return re.compile(pattern, flags)


    @staticmethod
    def search(
            pattern: Pattern[str],
            text: str
    ) -> bool | None:
        return pattern.search(text)

