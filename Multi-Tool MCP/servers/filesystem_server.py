"""File System MCP Server (stdio transport).

Tools: list_files, read_file, search_file, file_metadata

All relative paths are resolved against the project root (PROJECT_ROOT env var),
so the assistant always works inside the project directory by default.
"""

import fnmatch
import os
import time
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("filesystem")

PROJECT_ROOT = Path(
    os.environ.get("PROJECT_ROOT", str(Path(__file__).resolve().parents[1]))
).resolve()

MAX_RESULT_LINES = 200
MAX_FILE_BYTES = 1_000_000  # 1 MB safety limit for read_file

# Directories never worth listing (keeps results clean for the assistant)
IGNORED_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "logs",
}


def _is_ignored(path: Path) -> bool:
    try:
        rel_parts = path.relative_to(PROJECT_ROOT).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in IGNORED_DIRS for part in rel_parts)


def _resolve(path_str: str) -> Path:
    """Resolve a possibly-relative path against the project root."""
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        p = PROJECT_ROOT / p
    return p.resolve()


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _fmt_list(paths: list) -> str:
    if not paths:
        return "No files matched."
    shown = paths[:MAX_RESULT_LINES]
    body = "\n".join(shown)
    if len(paths) > MAX_RESULT_LINES:
        body += f"\n... ({len(paths) - MAX_RESULT_LINES} more not shown)"
    return body


@mcp.tool()
def list_files(directory: str = ".", pattern: str = "*", recursive: bool = False) -> str:
    """List files in a directory.

    Args:
        directory: Directory to list (relative paths resolve to the project root).
        pattern: Glob pattern, e.g. "*.py", "*.txt", or "**/*.py" for all depths.
        recursive: If True, search all subdirectories (equivalent to a "**/" prefix).

    Returns a newline-separated list of paths.
    """
    base = _resolve(directory)
    if not base.exists():
        raise ToolError(f"Directory not found: {_rel(base)}")
    if not base.is_dir():
        raise ToolError(f"Not a directory: {_rel(base)}")

    try:
        glob_pattern = f"**/{pattern}" if recursive and not pattern.startswith("**/") else pattern
        paths = sorted(
            p for p in base.glob(glob_pattern)
            if p.is_file() and not _is_ignored(p)
        )
    except Exception as e:  # pragma: no cover - defensive
        raise ToolError(f"Error listing files: {e}") from e

    return _fmt_list([_rel(p) for p in paths])


@mcp.tool()
def search_file(directory: str = ".", filename_pattern: str = "*.py") -> str:
    """Recursively find files whose NAME matches a pattern (like `find -name`).

    Args:
        directory: Directory to search (relative paths resolve to the project root).
        filename_pattern: Pattern matched against the file name only,
            e.g. "*.py", "*.json", "mcp_*".

    Returns a newline-separated list of matching paths.
    """
    base = _resolve(directory)
    if not base.exists():
        raise ToolError(f"Directory not found: {_rel(base)}")

    try:
        matches = sorted(
            p for p in base.rglob("*")
            if p.is_file() and fnmatch.fnmatch(p.name, filename_pattern) and not _is_ignored(p)
        )
    except Exception as e:  # pragma: no cover - defensive
        raise ToolError(f"Error searching files: {e}") from e

    return _fmt_list([_rel(p) for p in matches])


@mcp.tool()
def read_file(path: str, max_lines: int = 200) -> str:
    """Read a text file and return its contents.

    Args:
        path: File path (relative paths resolve to the project root).
        max_lines: Maximum number of lines to return (default 200).

    Returns the file content, truncated with a note if it is longer.
    """
    p = _resolve(path)
    if not p.exists():
        raise ToolError(f"File not found: {_rel(p)}")
    if p.is_dir():
        raise ToolError(f"Path is a directory, not a file: {_rel(p)}")
    if p.stat().st_size > MAX_FILE_BYTES:
        raise ToolError(f"File is larger than 1 MB ({p.stat().st_size} bytes): {_rel(p)}")

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        raise ToolError(f"Could not read file: {e}") from e

    lines = text.splitlines()
    truncated = len(lines) > max_lines
    body = "\n".join(lines[:max_lines])
    if truncated:
        body += f"\n... (file has {len(lines)} lines, showing first {max_lines})"
    return body or "(empty file)"


@mcp.tool()
def file_metadata(path: str) -> str:
    """Get metadata for a file or directory.

    Args:
        path: File or directory path (relative paths resolve to the project root).

    Returns type, size, and created/modified timestamps.
    """
    p = _resolve(path)
    if not p.exists():
        raise ToolError(f"Path not found: {_rel(p)}")

    st = p.stat()
    kind = "directory" if p.is_dir() else "file"
    return (
        f"path: {_rel(p)}\n"
        f"type: {kind}\n"
        f"size_bytes: {st.st_size}\n"
        f"extension: {p.suffix or '(none)'}\n"
        f"modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}\n"
        f"created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_ctime))}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
