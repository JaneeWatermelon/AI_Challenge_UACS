"""
@file agent/utils/paths.py
"""

import os
from pathlib import Path
from typing import List


class FsService:

    def __init__(self,
                 #TODO: environment
                 ):
        #self.environment = environment
        ...


    def resolve_path(self, path: Path) -> Path:
        ...


    def is_path_allowed(self, path: Path) -> bool:
        #TODO: environment checking
        ...


    def _path_assert(self, path: Path) -> None:
        full_path = self.resolve_path(path)
        if not self.is_path_allowed(full_path):
            raise ValueError(f"path is not allowed in the environment: {str(path)}")


    def _dir_assert(self, path: Path) -> None:
        full_path = self.resolve_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"directory not found: {str(path)}")

        if not full_path.is_dir():
            raise NotADirectoryError(f"expected path to a directory, given: {str(path)}")


    def _file_assert(self, path: Path) -> None:
        full_path = self.resolve_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"file not found: {str(path)}")

        if not full_path.is_file():
            raise NotADirectoryError(f"expected path to a file, given: {str(path)}")


    @staticmethod
    def validate_path(path: Path) -> bool:
        if len(str(path)) > 4096:
            return False

        try:
            path_obj = Path(path)
        except ValueError as e:
            return False

        if path_obj.is_absolute():
            return False

        return True


    def mkdir(self, path: Path, parents: bool=False) -> None:
        self._path_assert(path)

        full_path = self.resolve_path(path)

        full_path.mkdir(parents=parents, exist_ok=True)


    def listdir(self, path: Path) -> List[Path]:
        self._path_assert(path)
        self._dir_assert(path)

        full_path = self.resolve_path(path)

        return list(full_path.iterdir())


    def create_file(self, path: Path, content: List[str] | None=None) -> None:
        self._path_assert(path)

        full_path = self.resolve_path(path)
        if full_path.exists():
            raise RuntimeError(f"file already exists: {str(path)}")

        full_path.touch(exist_ok=False)

        if content is not None:
            full_path.write_text("\n".join(content))


    def remove(self, path: Path) -> None:
        self._path_assert(path)

        full_path = self.resolve_path(path)
        os.remove(full_path)


    def rename(self, path: Path, target: str) -> None:
        self._path_assert(path)

        full_path = self.resolve_path(path)

        full_path.rename(target)


    def readline(self, path: Path, idx: int) -> str:
        ...


    def readlines(self, path: Path, base: int, offset: int) -> List[str]:
        ...


    def insertline(self, path: Path, base: int, content: str) -> None:
        ...


    def appendline(self, path: Path, content: str) -> None:
        ...


    def insertlines(self, path: Path, base: int, content: List[str]) -> None:
        ...


    def appendlines(self, path: Path, content: List[str]) -> None:
        ...
