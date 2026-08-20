"""
@file agent/utils/regex.py
"""

import re
from re import Pattern, Match
from typing import Iterable, Iterator


class RegexService:

    @staticmethod
    def compile(
        pattern: str,
        *,
        regex: bool = True,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> Pattern[str]:
        if not regex:
            pattern = re.escape(pattern)

        if whole_word:
            pattern = rf"\b(?:{pattern})\b"

        flags = 0

        if not case_sensitive:
            flags |= re.IGNORECASE

        return re.compile(pattern, flags)


    @staticmethod
    def search(pattern: Pattern[str], text: str) -> Match[str] | None:
        return pattern.search(text)


    @staticmethod
    def finditer(pattern: Pattern[str], text: str) -> Iterator[Match[str]]:
        return pattern.finditer(text)


    @staticmethod
    def matches(pattern: Pattern[str], text: str) -> bool:
        return pattern.search(text) is not None
