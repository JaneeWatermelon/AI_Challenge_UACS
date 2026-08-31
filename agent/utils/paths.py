"""
@file agent/utils/paths.py
"""

import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.environment import Environment, EnvKeys
from utils.logger import get_logger

logger = get_logger(__name__)

class FsService:
    """
    Service providing a filesystem interface for the agent.

    All paths are resolved **relative to the workspace directory**
    """

    def __init__(self, workspace_dir: Optional[Path] = None):
        """
        Initialize the filesystem service.

        Args:
            workspace_dir: root directory of the agent's workspace.
                          If None, uses current working directory.
                          Absolute path
        """
        if workspace_dir is None:
            self._workspace_dir = Path(Environment.get(EnvKeys.LOCAL_AGENT_WORKDIR)).resolve() or Path.cwd()
        else:
            self._workspace_dir = Path(workspace_dir).resolve()

        # Ensure workspace directory exists
        self._workspace_dir.mkdir(parents=True, exist_ok=True)

    @property
    def workspace_dir(self) -> Path:
        """
        :return: the root directory of the agent's workspace.
        """
        return self._workspace_dir

    def resolve_path(self, path: Path) -> Path:
        """
        Resolve a path relative to the workspace directory.

        Example: ``"src/common.py"`` -> ``/workspace_dir/src/common.py``
        (if it exists).

        *Note:* this is for internal agent use only — never send a
        resolved (absolute) path back to the agent.

        :param path: workspace-root-relative path.
        :return: resolved absolute path.
        :raises: path outside workspace.
        """
        full_path = (self._workspace_dir / path).resolve()
        logger.info(f"self._workspace_dir: {self._workspace_dir}")
        logger.info(f"path: {path}")
        logger.info(f"self._workspace_dir / path: {self._workspace_dir / path}")
        logger.info(f"full_path: {full_path}")

        # Check if path is within workspace (security check)
        try:
            full_path.relative_to(self._workspace_dir)
        except ValueError:
            message = f"Path outside workspace: {path} | Workspace: {self._workspace_dir} | full_path: {full_path}"
            logger.exception(f"resolve_path: {message}")
            raise PermissionError(message)

        return full_path

    def _dir_assert(self, path: Path) -> Path:
        """
        Verify that a path points to an existing, allowed **directory**.

        :param path: workspace-relative path to a directory.
        :return Path: resolved dir path, if allowed.
        :raises FileNotFoundError: if the directory does not exist.
        :raises NotADirectoryError: if the path is not a directory.
        """
        full_path = self.resolve_path(path)

        if not full_path.is_dir():
            raise NotADirectoryError(f"expected path to a directory, given: {str(path)}")

        return full_path

    def _file_assert(self, path: Path) -> Path:
        """
        Verify that a path points to an existing, allowed **file**.

        :param path: workspace-relative path to a file.
        :raises FileNotFoundError: if the file does not exist.
        :raises ValueError: if the path is not a file.
        """
        full_path = self.resolve_path(path)

        if not full_path.is_file():
            raise ValueError(f"expected path to a file, given: {str(path)}")

        return full_path

    def listdir(self, path: Path, max_depth: int = 1) -> List[Path]:
        """
        Scan a directory for its entries, up to a maximum depth.

        :param path: workspace-relative directory path.
        :param max_depth: maximum depth of entries to include.
        :return: list of discovered entries.
        """
        full_path = self._dir_assert(path)
        result = []

        def _walk(current: Path, depth: int):
            if depth > max_depth:
                return
            try:
                for item in current.iterdir():
                    # Convert to relative path for result
                    rel_path = item.relative_to(self._workspace_dir)
                    result.append(rel_path)
                    if item.is_dir():
                        _walk(item, depth + 1)
            except PermissionError:
                # Skip directories without read permissions
                pass

        _walk(full_path, 1)
        return result

    def create_file(self,
                    path: Path,
                    content: List[str] | None = None
                    ) -> None:
        """
        Create a new file at an allowed path.

        :param path: workspace-relative path.
        :param content: optional initial content for the new file.
        :raises RuntimeError: if the file already exists.
        """
        full_path = self.resolve_path(path)

        if full_path.exists():
            raise RuntimeError(f"file already exists: {str(path)}")

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        full_path.touch(exist_ok=False)

        if content is not None:
            full_path.write_text("\n".join(content))

    def create_directory(self, path: Path) -> None:
        """
        Create a new directory at an allowed path.

        :param path: workspace-relative path.
        :raises RuntimeError: if the directory already exists.
        """
        full_path = self.resolve_path(path)

        if full_path.exists():
            raise RuntimeError(f"directory already exists: {str(path)}")

        full_path.mkdir(parents=True, exist_ok=False)

    def remove(self, path: Path) -> None:
        """
        Remove a file or directory.

        :param path: workspace-relative path to remove.
        """
        full_path = self.resolve_path(path)

        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()

    def get_metadata(self, path: Path) -> Dict[str, Any]:
        """
        Read general metadata for a file or directory.

        :param path: workspace-relative file or directory path.
        :return: a metadata mapping (``name``, ``path``, ``is_file``,
            ``is_dir``, ``size``, ``modified``, ``permissions``).
        """
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

        :param path: workspace-relative path to the file.
        :param base: 0-based line number to start reading from.
        :param offset: number of lines to read.
        :return: the read lines.
        """
        full_path = self._file_assert(path)

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Handle edge cases
        base = max(0, base)
        if base >= len(lines):
            return []

        end = min(base + offset, len(lines))
        # Strip newline characters but preserve empty lines
        return [line.rstrip('\n') for line in lines[base:end]]

    def insertlines(self, path: Path, base: int, content: List[str]) -> None:
        """
        Insert content at the specified line, **without** overwriting
        existing lines.

        :param path: workspace-relative path to the file.
        :param base: 0-based line number to insert at.
        :param content: lines to insert.
        """
        full_path = self._file_assert(path)

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Handle edge cases
        base = max(0, base)
        base = min(base, len(lines))

        # Insert content
        lines = lines[:base] + [line + '\n' for line in content] + lines[base:]

        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def appendlines(self, path: Path, content: List[str]) -> None:
        """
        Append content to the end of the file.

        :param path: workspace-relative path to the file.
        :param content: lines to append.
        """
        full_path = self._file_assert(path)

        with open(full_path, 'a', encoding='utf-8') as f:
            for line in content:
                f.write(line + '\n')

    def replacelines(self, path: Path, base: int, offset: int, content: List[str]) -> None:
        """
        Replace ``offset`` lines starting from ``base`` with ``content``.

        :param path: workspace-relative path to the file.
        :param base: 0-based line number to start replacing from.
        :param offset: number of lines to replace.
        :param content: lines to replace them with.
        """
        full_path = self._file_assert(path)

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Handle edge cases
        base = max(0, base)
        if base >= len(lines):
            # If base beyond end, just append
            lines.extend([line + '\n' for line in content])
        else:
            end = min(base + offset, len(lines))
            # Replace the range
            lines[base:end] = [line + '\n' for line in content]

        with open(full_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
