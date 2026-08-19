"""
@file agent/utils/paths.py
"""

from pathlib import Path
from typing import List


class FsService:

    def __init__(self,
                 #env
                 ):
        ...


    def is_path_allowed(self, path: Path) -> bool:
        #TODO: environment checking
        ...


    @staticmethod
    def validate_path(path: Path) -> bool:
        ...


    def mkdir(self, path: Path, parents: bool=False) -> None:
        ...


    def listdir(self, directory: Path) -> List[Path]:
        ...


    def create_file(self, path: Path, content) -> None:
        ...


    def remove(self, path: Path) -> None:
        ...


    def readline(self, path: Path, idx: int) -> str:
        ...


    def readlines(self, path: Path, base: int, offset: int) -> List[str]:
        ...


    def insertline(self, path: Path, idx: int, content: str) -> None:
        ...


    def appendline(self, path: Path, content: str) -> None:
        ...


    def insertlines(self, path: Path, idx: int, content: List[str]) -> None:
        ...


    def appendlines(self, path: Path, content: List[str]) -> None:
        ...
