"""
@file agent/models/record.py
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Record:
    filename: str
    base: int
    content: List[str]
