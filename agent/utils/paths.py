"""
@file agent/utils/paths.py
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class FsService:
    """
    служба предоставляющая интерфейс
    для работы с файловой системой
    пути разрешаются относительно рабочей директории (TODO: self.environment)
    """

    def __init__(self,
                 #TODO: environment
                 ):
        #self.environment = environment
        ...


    @property
    def workspace_dir(self) -> Path:
        """
        :return: the root directory of agent's workspace
        """
        ...


    def resolve_path(self, path: Path) -> Path:
        """
        resolves path relative environment workspace
        e.g.    agent request: "src/common.py";
                resolved path: /workspace_dir/src/common.py (if  exists)
        only for agent using! don't send resolved path!
        :exception: file or directory does not exist
        :param path: workspace root relative path
        :return: resolved absolute path
        """
        ...


    def is_path_allowed(self, path: Path) -> bool:
        """
        path exists relative workspace dir check
        :param path: workspace dir relative path
        :return:    True - exists, False otherwise
        """
        #TODO: environment checking
        ...


    def _path_assert(self, path: Path) -> Path:
        """
        path resolution wrapper with check
        :exception: PermissionError if path does noe exist
        :param path: relative path
        :return: resolved path if it's allowed
        """
        full_path = self.resolve_path(path)

        if not self.is_path_allowed(full_path):
            raise PermissionError(f"path is not allowed in the environment: {str(path)}")

        return full_path


    def _dir_assert(self, path: Path) -> None:
        """
        directory path check with allowing check
        :exception: FileNotFoundError, NotADirectoryError
        :param path: relative path to directory
        :return: None
        """
        full_path = self._path_assert(path)

        if not full_path.exists():
            raise FileNotFoundError(f"directory not found: {str(path)}")

        if not full_path.is_dir():
            raise NotADirectoryError(f"expected path to a directory, given: {str(path)}")


    def _file_assert(self, path: Path) -> None:
        """
        file path check with allowing check
        :exception: FileNotFoundError, ValueError
        :param path: relative path to directory
        :return: None
        """
        full_path = self._path_assert(path)

        if not full_path.exists():
            raise FileNotFoundError(f"file not found: {str(path)}")

        if not full_path.is_file():
            raise ValueError(f"expected path to a file, given: {str(path)}")


    @staticmethod
    def validate_path(path: Path) -> tuple[bool, str, Optional[Path]]:
        """
        environment independent path pre-check
        :param path: relative path
        :return: is valid flag, message, path or None if check failed
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
        make directory relative workspace directory
        :param path:    path to a new directory
        :param parents: -p mkdir flag
        :return: None
        """
        self._path_assert(path)

        full_path = self.resolve_path(path)

        full_path.mkdir(parents=parents, exist_ok=True)


    def listdir(self, path: Path, max_depth: int) -> List[Path]:
        """
        scanning directory's endpoints
        :param path: allowed directory path
        :param max_depth: max depth of included endpoints
        :return: list of founded endpoints
        """
        self._path_assert(path)
        self._dir_assert(path)  # file has not relative endpoints

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
        create file by allowed path
        :exception: RuntimeError
        :param path: workspace root relative path
        :param content: content of the new file
        :return: None
        """
        self._path_assert(path) # is path workspace root relative

        full_path = self.resolve_path(path)
        if full_path.exists():
            raise RuntimeError(f"file already exists: {str(path)}")

        full_path.touch(exist_ok=False)

        if content is not None:
            full_path.write_text("\n".join(content))


    def remove(self, path: Path) -> None:
        """
        #TODO: directory removing check (recursively flag)
        remove file or directory
        :param path:
        :return:
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
        general file or directory metadata reading
        :param path: allowed file or directory
        :return: metadata map
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
        reading offset lines starting from the base
        :param path: путь к файлу
        :param base: строка, с которой начинаем читать (0-based)
        :param offset: сколько строк прочитать
        :return: список строк
        """
        ...

    def insertlines(self, path: Path, base: int, content: List[str]) -> None:
        """
        insert content at the specified line
        :param path: путь к файлу
        :param base: строка, куда вставляем (0-based)
        :param content: список строк для вставки
        :return: None
        """
        ...

    def appendlines(self, path: Path, content: List[str]) -> None:
        """
        append content to the end of the file
        :param path: путь к файлу
        :param content: список строк для добавления
        :return: None
        """
        ...

    def replacelines(self, path: Path, base: int, offset: int, content: List[str]) -> None:
        """
        replace offset lines starting from base with content
        :param path: путь к файлу
        :param base: строка, с которой начинаем заменять (0-based)
        :param offset: сколько строк заменяем
        :param content: список строк, на которые заменяем
        :return: None
        """
        ...