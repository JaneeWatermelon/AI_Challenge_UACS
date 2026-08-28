"""
@file agent/actions/tools/cmd/exec.py
"""

import os
import platform
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.paths import FsService
from utils.assertion import safe_verdict
from actions.register import ActionRegister


DEFAULT_TIMEOUT = 5

_OS = platform.system()  # "Linux" | "Darwin" | "Windows"
_IS_WINDOWS = _OS == "Windows"

_LOOPBACK_HOSTS = {"127.0.0.1", "::1", "localhost"}

_GLOBAL_LOG_DIRS_BY_OS = {
    "Linux": ("/var/log",),
    "Darwin": ("/var/log",),
    "Windows": (),  # events reading by wevtutil only, not files
}

_PATH_READING_COMMANDS = {"cat", "tail", "head", "grep"}


Validator = Callable[[List[str]], None]


def _no_positional(args: List[str]) -> None:
    positional = [a for a in args if not a.startswith(("-", "/"))]
    if positional:
        raise PermissionError(f"positional arguments are not allowed: {positional}")


def _denied_flags(denied: Set[str]) -> Validator:
    def _v(args: List[str]) -> None:
        hit = [a for a in args if a in denied]
        if hit:
            raise PermissionError(f"flags not allowed: {hit}")
    return _v


def _denied_words(denied: Set[str]) -> Validator:
    def _v(args: List[str]) -> None:
        hit = [a for a in args if a.lower() in denied]
        if hit:
            raise PermissionError(f"arguments not allowed: {hit}")
    return _v


def _loopback_target_only(args: List[str]) -> None:
    targets = [a for a in args if not a.startswith(("-", "/"))]
    if not targets:
        raise ValueError("target host is required")
    target = targets[-1]
    if target.lower() not in _LOOPBACK_HOSTS:
        raise PermissionError(
            f"only local targets are allowed ({', '.join(sorted(_LOOPBACK_HOSTS))}), got: {target}"
        )


def _wmic_validator(args: List[str]) -> None:
    allowed_aliases = {"os", "cpu", "logicaldisk", "computersystem", "qfe", "service", "startup", "product"}
    allowed_verbs = {"get", "list"}
    denied_tokens = {"call", "delete", "set"}

    non_flag = [a for a in args if not a.startswith("/")]
    if any(a.lower() in denied_tokens for a in args):
        raise PermissionError("wmic verb not allowed (only get/list are permitted)")
    if any(a.lower().startswith("/node") for a in args):
        raise PermissionError("wmic remote targeting (/node:) is not allowed")
    if not non_flag or non_flag[0].lower() not in allowed_aliases:
        raise PermissionError(f"wmic alias not allowed (allowed: {', '.join(sorted(allowed_aliases))})")
    if not any(a.lower() in allowed_verbs for a in non_flag[1:]):
        raise PermissionError("wmic command must use 'get' or 'list'")


def _wevtutil_validator(args: List[str]) -> None:
    allowed = {"qe", "gl", "el"}
    subcommand = next((a for a in args if not a.startswith("/")), None)
    if subcommand not in allowed:
        raise PermissionError(f"wevtutil subcommand not allowed (allowed: {', '.join(sorted(allowed))})")


_CROSS_PLATFORM: Dict[str, Optional[Validator]] = {
    "hostname": _no_positional,
    "whoami": None,
    "date": _denied_flags({"-s", "--set"}),
    "echo": None,
    "ping": _loopback_target_only,
    "nslookup": _loopback_target_only,
    "which": None,
    "where": None,
}


_LINUX_ONLY: Dict[str, Optional[Validator]] = {
    "uname": None,
    "uptime": None,
    "ps": None,
    "ip": _denied_words({"add", "del", "delete", "change", "replace", "flush", "set", "addlabel"}),
    "ss": None,
    "journalctl": _denied_flags({
        "--vacuum-time", "--vacuum-size", "--vacuum-files",
        "--rotate", "--flush", "--sync", "--relinquish-var",
    }),
    "dmesg": _denied_flags({"-C", "--clear", "-c", "--read-clear"}),
    "last": None,
    "lastb": None,
    "who": None,
    "w": None,
}


_MACOS_ONLY: Dict[str, Optional[Validator]] = {
    "uname": None,
    "uptime": None,
    "ps": None,
    "ifconfig": _denied_words({"up", "down", "delete", "del", "destroy", "add", "alias", "-alias"}),
    "netstat": None,
}


_WINDOWS_ONLY: Dict[str, Optional[Validator]] = {
    "wmic": _wmic_validator,
    "tasklist": None,
    "ipconfig": _denied_flags({"/release", "/release6", "/renew", "/renew6", "/registerdns", "/setclassid"}),
    "netstat": None,
    "wevtutil": _wevtutil_validator,
}


_OS_SPECIFIC = {"Linux": _LINUX_ONLY, "Darwin": _MACOS_ONLY, "Windows": _WINDOWS_ONLY}


@ActionRegister.register("exec")
class ActionExec(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService=FsService()):
        allowed = self._allowed_commands()
        summary = ", ".join(sorted(set(allowed) | _PATH_READING_COMMANDS))
        super().__init__(
            ActionExec._registered_name,
            "reads global system/security diagnostics and logs via a fixed set of "
            "read-only utilities (OS-dependent). Never reads or touches anything "
            "inside the project workspace - use fs actions for that. Arguments:\n"
            "command - the command string to execute (required)\n"
            "timeout - max execution time in seconds (default: 15)\n"
            f"p.s. no shell, no pipes/chaining, allowed commands on this OS: {summary}",
            arguments,
            # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            # CONTRACT, DO NOT ADD ANY NON-READONLY COMMAND v
            # -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
            True
        )
        self.fs = fs_service


    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }


    @staticmethod
    def _allowed_commands() -> Dict[str, Optional[Validator]]:
        return {**_CROSS_PLATFORM, **_OS_SPECIFIC.get(_OS, {})}


    @staticmethod
    def _global_log_dirs() -> tuple:
        return _GLOBAL_LOG_DIRS_BY_OS.get(_OS, ())


    @staticmethod
    def _is_under(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True

        except ValueError:
            return False


    def _assert_path_arg_is_global(self, raw_arg: str) -> None:
        resolved = Path(os.path.realpath(raw_arg))

        workspace = Path(os.path.realpath(str(self.fs.workspace_dir)))
        if self._is_under(resolved, workspace):
            raise PermissionError(f"exec is not allowed to read workspace files: {raw_arg}")

        allowed_dirs = self._global_log_dirs()
        if not any(self._is_under(resolved, Path(os.path.realpath(d))) for d in allowed_dirs):
            raise PermissionError(
                f"path is outside allowed global log directories {allowed_dirs}: {raw_arg}"
            )


    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        command = self.arguments.get("command")
        if not command or not isinstance(command, str):
            raise ValueError("argument 'command' is required and must be a non-empty string")

        timeout = self.arguments.get("timeout", DEFAULT_TIMEOUT)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("argument 'timeout' must be a positive number")

        try:
            args = shlex.split(command, posix=not _IS_WINDOWS)
        except ValueError as e:
            raise ValueError(f"could not parse command: {e}")

        if not args:
            raise ValueError("empty command")

        exe = Path(args[0]).name.lower()
        if _IS_WINDOWS and exe.endswith((".exe", ".cmd", ".bat")):
            exe = exe.rsplit(".", 1)[0]

        rest = args[1:]

        if exe in _PATH_READING_COMMANDS:
            path_args = [a for a in rest if not a.startswith("-")]
            if not path_args:
                raise ValueError(f"'{exe}' requires at least one file path argument")
            for p in path_args:
                self._assert_path_arg_is_global(p)
        else:
            allowed = self._allowed_commands()
            if exe not in allowed:
                raise PermissionError(f"command not allowed on {_OS}: {exe}")

            validator = allowed[exe]
            if validator is not None:
                validator(rest)

        try:
            result = subprocess.run(
                args,
                shell=False,                # '|', ':', '`' and so on is forbidden
                cwd=tempfile.gettempdir(),  # neutral directory
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )

        except subprocess.TimeoutExpired:
            return ActionVerdict(
                ExitCode.EXECUTION_ERROR,
                f"command timed out after {timeout}s",
            )

        except FileNotFoundError:
            raise FileNotFoundError(f"executable not found: {exe}")

        return ActionVerdict(
            ExitCode.SUCCESS,
            "command executed",
            {
                "exitcode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )


    @override
    def reverse(self) -> "ActionExec":
        """
        read only action (see `self.__init__`)
        """
        return self
