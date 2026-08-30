"""
@file agent/actions/code/import_collector.py
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from utils.assertion import safe_verdict
from utils.paths import FsService
from actions.register import ActionRegister


class ImportKeyword(Enum):
    IMPORT = "import"
    INCLUDE = "#include"
    USING = "using"
    USE = "use"
    REQUIRE = "require"
    REQUIRE_RELATIVE = "require_relative"
    EXTERN_CRATE = "extern crate"
    SOURCE = "source"
    DOT_SOURCE = "."
    COMPTIME = "comptime"
    LIBRARY = "library"


IMPORT_KEYWORDS = {
    # Python
    ".py": ImportKeyword.IMPORT,
    ".pyw": ImportKeyword.IMPORT,
    ".pyi": ImportKeyword.IMPORT,
    ".pyx": ImportKeyword.IMPORT,

    # JavaScript / TypeScript
    ".js": ImportKeyword.IMPORT,
    ".mjs": ImportKeyword.IMPORT,
    ".cjs": ImportKeyword.IMPORT,
    ".jsx": ImportKeyword.IMPORT,
    ".ts": ImportKeyword.IMPORT,
    ".tsx": ImportKeyword.IMPORT,

    # Java / Kotlin / Scala
    ".java": ImportKeyword.IMPORT,
    ".kt": ImportKeyword.IMPORT,
    ".kts": ImportKeyword.IMPORT,
    ".scala": ImportKeyword.IMPORT,

    # Go
    ".go": ImportKeyword.IMPORT,

    # Rust
    ".rs": ImportKeyword.USE,

    # PHP
    ".php": ImportKeyword.USE,

    # Ruby
    ".rb": ImportKeyword.REQUIRE,
    ".rbw": ImportKeyword.REQUIRE,

    # Perl
    ".pl": ImportKeyword.USE,
    ".pm": ImportKeyword.USE,

    # Swift
    ".swift": ImportKeyword.IMPORT,

    # C / C++ (and Arduino)
    ".c": ImportKeyword.INCLUDE,
    ".cpp": ImportKeyword.INCLUDE,
    ".cc": ImportKeyword.INCLUDE,
    ".cxx": ImportKeyword.INCLUDE,
    ".h": ImportKeyword.INCLUDE,
    ".hpp": ImportKeyword.INCLUDE,
    ".hxx": ImportKeyword.INCLUDE,
    ".ino": ImportKeyword.INCLUDE,

    # C#
    ".cs": ImportKeyword.USING,

    # Zig
    ".zig": ImportKeyword.COMPTIME,
    ".zir": ImportKeyword.COMPTIME,

    # Nim
    ".nim": ImportKeyword.IMPORT,

    # Julia
    ".jl": ImportKeyword.IMPORT,

    # R
    ".r": ImportKeyword.LIBRARY,
    ".rds": ImportKeyword.LIBRARY,

    # Erlang / Elixir
    ".erl": ImportKeyword.IMPORT,
    ".hrl": ImportKeyword.INCLUDE,
    ".ex": ImportKeyword.IMPORT,
    ".exs": ImportKeyword.IMPORT,

    # Shell
    ".sh": ImportKeyword.SOURCE,
    ".bash": ImportKeyword.SOURCE,
    ".zsh": ImportKeyword.SOURCE,

    # SQL
    ".sql": ImportKeyword.INCLUDE,
    ".pgsql": ImportKeyword.INCLUDE,

    # Markdown / Config
    ".md": ImportKeyword.INCLUDE,
    ".yaml": ImportKeyword.IMPORT,
    ".yml": ImportKeyword.IMPORT,
    ".toml": ImportKeyword.IMPORT,

    # SystemVerilog / Verilog
    ".sv": ImportKeyword.INCLUDE,
    ".v": ImportKeyword.INCLUDE,
    ".vh": ImportKeyword.INCLUDE,
}


class ImportKeyword(Enum):
    IMPORT = "import"
    INCLUDE = "#include"
    USING = "using"
    USE = "use"
    REQUIRE = "require"
    REQUIRE_RELATIVE = "require_relative"
    EXTERN_CRATE = "extern crate"
    SOURCE = "source"
    DOT_SOURCE = "."
    COMPTIME = "comptime"
    LIBRARY = "library"


def _parse_python(lines: list[str]) -> list[str]:
    result = []
    keyword = ImportKeyword.IMPORT.value
    from_keyword = "from"

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(keyword + " ") or stripped.startswith(from_keyword + " "):
            result.append(stripped)

    return result


def _parse_c_cpp(lines: list[str]) -> list[str]:
    result = []
    keyword = ImportKeyword.INCLUDE.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(keyword + " "):
            result.append(stripped)

    return result


def _parse_csharp(lines: list[str]) -> list[str]:
    result = []
    keyword = ImportKeyword.USING.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(keyword + " "):
            result.append(stripped)

    return result


def _parse_ruby(lines: list[str]) -> list[str]:
    result = []
    require = ImportKeyword.REQUIRE.value
    require_relative = ImportKeyword.REQUIRE_RELATIVE.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(require + " ") or stripped.startswith(require_relative + " "):
            result.append(stripped)

    return result


def _parse_rust(lines: list[str]) -> list[str]:
    result = []
    use = ImportKeyword.USE.value
    extern_crate = ImportKeyword.EXTERN_CRATE.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(use + " ") or stripped.startswith(extern_crate + " "):
            result.append(stripped)

    return result


def _parse_shell(lines: list[str]) -> list[str]:
    result = []
    source = ImportKeyword.SOURCE.value
    dot_source = ImportKeyword.DOT_SOURCE.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(source + " ") or stripped.startswith(dot_source + " "):
            result.append(stripped)

    return result


def _parse_generic_import(lines: list[str]) -> list[str]:
    result = []
    keyword = ImportKeyword.IMPORT.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(keyword + " "):
            result.append(stripped)

    return result


def _parse_generic_include(lines: list[str]) -> list[str]:
    result = []
    keyword = ImportKeyword.INCLUDE.value

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(keyword + " "):
            result.append(stripped)

    return result


PARSERS = {
    # Python
    ".py": _parse_python,
    ".pyw": _parse_python,
    ".pyi": _parse_python,
    ".pyx": _parse_python,

    # C / C++
    ".c": _parse_c_cpp,
    ".cpp": _parse_c_cpp,
    ".cc": _parse_c_cpp,
    ".cxx": _parse_c_cpp,
    ".h": _parse_c_cpp,
    ".hpp": _parse_c_cpp,
    ".hxx": _parse_c_cpp,
    ".ino": _parse_c_cpp,

    # C#
    ".cs": _parse_csharp,

    # Ruby
    ".rb": _parse_ruby,
    ".rbw": _parse_ruby,

    # Rust
    ".rs": _parse_rust,

    # Shell
    ".sh": _parse_shell,
    ".bash": _parse_shell,
    ".zsh": _parse_shell,

    # Java / Kotlin / Scala
    ".java": _parse_generic_import,
    ".kt": _parse_generic_import,
    ".kts": _parse_generic_import,
    ".scala": _parse_generic_import,

    # Go
    ".go": _parse_generic_import,

    # PHP
    ".php": _parse_generic_import,

    # Swift
    ".swift": _parse_generic_import,

    # Nim
    ".nim": _parse_generic_import,

    # Julia
    ".jl": _parse_generic_import,

    # R
    ".r": _parse_generic_import,

    # Erlang / Elixir
    ".erl": _parse_generic_import,
    ".ex": _parse_generic_import,
    ".exs": _parse_generic_import,

    # SQL
    ".sql": _parse_generic_include,
    ".pgsql": _parse_generic_include,

    # Markdown / Config
    ".md": _parse_generic_include,
    ".yaml": _parse_generic_import,
    ".yml": _parse_generic_import,
    ".toml": _parse_generic_import,

    # SystemVerilog / Verilog
    ".sv": _parse_c_cpp,
    ".v": _parse_c_cpp,
    ".vh": _parse_c_cpp,

    # JavaScript / TypeScript
    ".js": _parse_generic_import,
    ".mjs": _parse_generic_import,
    ".cjs": _parse_generic_import,
    ".jsx": _parse_generic_import,
    ".ts": _parse_generic_import,
    ".tsx": _parse_generic_import,
}


@ActionRegister.register("collect_imports")
class ActionCollectImports(Action):

    def __init__(self,
                 arguments: Dict[str, Any],
                 fs_service: FsService = FsService()):
        super().__init__(
            ActionCollectImports._registered_name,
            "collects import/include/using statements from source files, arguments:\n"
            "files - list of file paths to analyze (required)\n"
            "returns: mapping file_path -> list of import/include/using statements found",
            arguments,
            True
        )
        self.fs = fs_service

    @staticmethod
    def keyword_by_file(filename: str) -> ImportKeyword | None:
        ext = Path(filename).suffix.lower()
        return IMPORT_KEYWORDS.get(ext)

    @override
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }

    @override
    @safe_verdict
    def execute(self) -> ActionVerdict:
        files = self.arguments.get("files", [])

        if not files:
            return ActionVerdict(
                ExitCode.MISSED_ARGUMENT,
                "missed 'files' argument"
            )

        result = {}

        for file in files:
            path = Path(file)
            parser = PARSERS.get(path.suffix.lower())

            if parser is None:
                continue

            try:
                content = path.read_text(encoding="utf-8")
                imports = parser(content.splitlines())

                if imports:
                    result[str(path)] = imports

            except Exception:
                continue

        return ActionVerdict(
            ExitCode.SUCCESS,
            "Imports collected",
            {"imports": result}
        )

    @override
    @safe_verdict
    def reverse(self) -> "ActionCollectImports":
        """
        read only action
        """
        return self
