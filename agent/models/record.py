"""
@file agent/models/record.py
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Record:

    base: int
    content: List[str]
