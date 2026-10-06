"""MCP client: maintains connections to multiple MCP servers over stdio.

Each server runs as a child process; its tools are discovered with
``list_tools`` at startup and later called through ``call_tool``.
"""

import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .logger import get_logger

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MCPServerConnection:
    """A single persistent connection to one MCP server process."""

    def __init__(self, name: str, script: Path):
        self.name = name
        self.script = Path(script)
        self.session: ClientSession | None = None
        self.tools = []
        self.available = False
        self.error: str | None = None

        env = {**os.environ, "PROJECT_ROOT": str(PROJECT_ROOT)}
        self.params = StdioServerParameters(
            command=sys.executable,
            args=[str(self.script)],
            env=env,
            cwd=str(PROJECT_ROOT),
        )
        self._stdio_ctx = None
        self._session_ctx = None

    async def start(self) -> None:
        """Spawn the server process and initialize an MCP session."""
        log = get_logger()
        try:
            self._stdio_ctx = stdio_client(self.params)
            read, write = await self._stdio_ctx.__aenter__()
            self._session_ctx = ClientSession(read, write)
            self.session = await self._session_ctx.__aenter__()
            await self.session.initialize()

            listed = await self.session.list_tools()
            self.tools = list(listed.tools)
            self.available = True
            self.error = None
            tool_names = ", ".join(t.name for t in self.tools) or "(none)"
            log.info("Connected to MCP server '%s' -> tools: %s", self.name, tool_names)
        except Exception as e:
            self.available = False
            self.error = str(e)
            log.error("MCP server '%s' is unavailable: %s", self.name, e)
            await self.stop()

    async def stop(self) -> None:
        """Close the session and terminate the server process (best effort)."""
        for ctx in (self._session_ctx, self._stdio_ctx):
            if ctx is None:
                continue
            try:
                await ctx.__aexit__(None, None, None)
            except Exception:  # pragma: no cover - shutdown is best effort
                pass
        self._session_ctx = None
        self._stdio_ctx = None
        self.session = None
        self.available = False


class MCPManager:
    """Starts/stops every configured MCP server and exposes their sessions."""

    def __init__(self, servers: dict[str, Path]):
        self.connections: dict[str, MCPServerConnection] = {
            name: MCPServerConnection(name, script) for name, script in servers.items()
        }

    async def start(self) -> None:
        for conn in self.connections.values():
            await conn.start()

    async def stop(self) -> None:
        for conn in self.connections.values():
            await conn.stop()

    def summary(self) -> str:
        lines = []
        for name, conn in self.connections.items():
            status = f"connected ({len(conn.tools)} tools)" if conn.available else f"DOWN ({conn.error})"
            lines.append(f"  - {name}: {status}")
        return "\n".join(lines)
