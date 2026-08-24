"""
@file agent/utils/paths.py
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class FsService:
    """
    Service providing a filesystem interface for the agent.

    All paths are resolved **relative to the workspace directory**
    (TODO: ``self.environment``).
    """

    def __init__(self,
                 #TODO: environment
                 ):
        #self.environment = environment
        ...


    @property
    def workspace_dir(self) -> Path:
        """
        :return: the root directory of the agent's workspace.
        """
        ...


    def resolve_path(self, path: Path) -> Path:
        """
        Resolve a path relative to the workspace directory.

        Example: ``"src/common.py"`` -> ``/workspace_dir/src/common.py``
        (if it exists).

        *Note:* this is for internal agent use only — never send a
        resolved (absolute) path back to the agent.

        :param path: workspace-root-relative path.
        :return: resolved absolute path.
        :raises: file or directory does not exist.
        """
        ...


    def is_path_allowed(self, path: Path) -> bool:
        """
        Check whether a path exists relative to the workspace directory.

        :param path: workspace-relative path.
        :return: ``True`` if it exists, ``False`` otherwise.
        """
        #TODO: environment checking
        ...


    def _path_assert(self, path: Path) -> Path:
        """
        Resolve a path and verify it is allowed.

        :param path: relative path.
        :return: resolved path, if allowed.
        :raises PermissionError: if the path is not allowed in the environment.
        """
        full_path = self.resolve_path(path)

        if not self.is_path_allowed(full_path):
            raise PermissionError(f"path is not allowed in the environment: {str(path)}")

        return full_path


    def _dir_assert(self, path: Path) -> None:
        """
        Verify that a path points to an existing, allowed **directory**.

        :param path: relative path to a directory.
        :raises FileNotFoundError: if the directory does not exist.
        :raises NotADirectoryError: if the path is not a directory.
        """
        full_path = self._path_assert(path)

        if not full_path.exists():
            raise FileNotFoundError(f"directory not found: {str(path)}")

        if not full_path.is_dir():
            raise NotADirectoryError(f"expected path to a directory, given: {str(path)}")


    def _file_assert(self, path: Path) -> None:
        """
        Verify that a path points to an existing, allowed **file**.

        :param path: relative path to a file.
        :raises FileNotFoundError: if the file does not exist.
        :raises ValueError: if the path is not a file.
        """
        full_path = self._path_assert(path)

        if not full_path.exists():
            raise FileNotFoundError(f"file not found: {str(path)}")

        if not full_path.is_file():
            raise ValueError(f"expected path to a file, given: {str(path)}")


    @staticmethod
    def validate_path(path: Path) -> tuple[bool, str, Optional[Path]]:
        """
        Environment-independent sanity check for a relative path.

        Checks length, validity, existence, and that the path is
        **not** absolute — absolute navigation is forbidden.

        :param path: relative path.
        :return: a tuple of ``(is_valid, message, path_or_none)``.
        """
        if len(str(path)) > 4096:
            return False, "too long path", None

        try:
            path_obj = Path(path)
        except ValueError as e:
            return False, f"invalid path: {str(e)}", None

        if not path.exists():
            return False, "file or directory is not exists", None

        if path_obj.is_absolute():
            return False, "absolute navigation is forbidden", None

        return True, "ok", path


    def mkdir(self, path: Path, parents: bool=False) -> None:
        """
        Create a directory relative to the workspace directory.

        :param path: path to the new directory.
        :param parents: equivalent to ``mkdir -p``.
        """
        self._path_assert(path)

        full_path = self.resolve_path(path)

        full_path.mkdir(parents=parents, exist_ok=True)


    def listdir(self, path: Path, max_depth: int) -> List[Path]:
        """
        Scan a directory for its entries, up to a maximum depth.

        :param path: allowed directory path.
        :param max_depth: maximum depth of entries to include.
        :return: list of discovered entries.
        """
        self._path_assert(path)
        self._dir_assert(path)  # a file has no relative entries

        full_path = self.resolve_path(path)
        result = []

        def _walk(current: Path, depth: int):
            if depth > max_depth:
                return
            for item in current.iterdir():
                result.append(item)
                if item.is_dir():
                    _walk(item, depth + 1)

        _walk(full_path, 1)
        return result


    def create_file(self,
                    path: Path,
                    content: List[str] | None=None
            ) -> None:
        """
        Create a new file at an allowed path.

        :param path: workspace-root-relative path.
        :param content: optional initial content for the new file.
        :raises RuntimeError: if the file already exists.
        """
        self._path_assert(path) # is the path workspace-root-relative?

        full_path = self.resolve_path(path)
        if full_path.exists():
            raise RuntimeError(f"file already exists: {str(path)}")

        full_path.touch(exist_ok=False)

        if content is not None:
            full_path.write_text("\n".join(content))


    def remove(self, path: Path) -> None:
        """
        Remove a file or directory.

        #TODO: add a recursive flag / check for directory removal.

        :param path: workspace-relative path to remove.
        """
        self._path_assert(path)

        full_path = self.resolve_path(path)
        os.remove(full_path)


    def rename(self, path: Path, target: str) -> None:
        """
        #TODO: DEPRECATED
        """
        self._path_assert(path)

        full_path = self.resolve_path(path)

        full_path.rename(target)


    def get_metadata(self, path: Path) -> Dict[str, Any]:
        """
        Read general metadata for a file or directory.

        :param path: allowed file or directory path.
        :return: a metadata mapping (``name``, ``path``, ``is_file``,
            ``is_dir``, ``size``, ``modified``, ``permissions``).
        """
        self._path_assert(path)

        full_path = self.resolve_path(path)
        stat = full_path.stat()

        return {
            "name": full_path.name,
            "path": str(full_path),
            "is_file": full_path.is_file(),
            "is_dir": full_path.is_dir(),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "permissions": oct(stat.st_mode)[-3:],
        }

    def readlines(self, path: Path, base: int, offset: int) -> List[str]:
        """
        Read ``offset`` lines starting from ``base``.

        :param path: path to the file.
        :param base: 0-based line number to start reading from.
        :param offset: number of lines to read.
        :return: the read lines.
        """
        ...

    def insertlines(self, path: Path, base: int, content: List[str]) -> None:
        """
        Insert content at the specified line, **without** overwriting
        existing lines.

        :param path: path to the file.
        :param base: 0-based line number to insert at.
        :param content: lines to insert.
        """
        ...

    def appendlines(self, path: Path, content: List[str]) -> None:
        """
        Append content to the end of the file.

        :param path: path to the file.
        :param content: lines to append.
        """
        ...

    def replacelines(self, path: Path, base: int, offset: int, content: List[str]) -> None:
        """
        Replace ``offset`` lines starting from ``base`` with ``content``.

        :param path: path to the file.
        :param base: 0-based line number to start replacing from.
        :param offset: number of lines to replace.
        :param content: lines to replace them with.
        """
        ...