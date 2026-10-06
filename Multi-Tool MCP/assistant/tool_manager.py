"""Tool registry: merges tools from all MCP servers and executes them with logging."""

import json
import time

from .logger import get_logger
from .mcp_client import MCPManager


class ToolManager:
    def __init__(self, manager: MCPManager):
        self.manager = manager
        self.registry: dict[str, str] = {}  # tool name -> server name
        self.schemas: dict[str, dict] = {}  # tool name -> MCP tool object

    async def refresh(self) -> dict[str, str]:
        """Rebuild the common tool registry from every available server."""
        self.registry.clear()
        self.schemas.clear()
        for server_name, conn in self.manager.connections.items():
            if not conn.available:
                continue
            for tool in conn.tools:
                if tool.name in self.registry:
                    get_logger().warning(
                        "Tool name collision: '%s' defined on both '%s' and '%s' - keeping '%s'",
                        tool.name, self.registry[tool.name], server_name, self.registry[tool.name],
                    )
                    continue
                self.registry[tool.name] = server_name
                self.schemas[tool.name] = tool
        return self.registry

    # ------------------------------------------------------------------ prompt
    def describe_tools(self) -> str:
        """Render the full tool list (name, description, arguments) for the LLM."""
        blocks = []
        for name, server in self.registry.items():
            tool = self.schemas[name]
            schema = getattr(tool, "inputSchema", {}) or {}
            props = schema.get("properties", {}) or {}
            required = set(schema.get("required", []) or [])
            if props:
                args = ", ".join(
                    f"{p}: {spec.get('type', 'any')}{' (required)' if p in required else ''}"
                    f" - {spec.get('description', '')}".strip()
                    for p, spec in props.items()
                )
            else:
                args = "(no arguments)"
            desc = (getattr(tool, "description", "") or "").strip().splitlines()[0]
            blocks.append(f"- {name} [server: {server}]\n    {desc}\n    args: {args}")
        return "\n".join(blocks) if blocks else "(no tools available)"

    def tool_names(self) -> list[str]:
        return sorted(self.registry)

    # ---------------------------------------------------------------- execute
    async def execute(self, tool_name: str, arguments: dict | None) -> dict:
        """Call a tool and return a uniform result dict (never raises)."""
        log = get_logger()
        arguments = arguments or {}
        start = time.perf_counter()

        def _done(payload: dict) -> dict:
            payload["execution_time"] = round(time.perf_counter() - start, 4)
            return payload

        server = self.registry.get(tool_name)
        if server is None:
            log.error("Tool: %s\nError: tool not found (available: %s)", tool_name, ", ".join(self.tool_names()))
            return _done({
                "success": False,
                "tool": tool_name,
                "server": None,
                "arguments": arguments,
                "error": f"Tool not found: '{tool_name}'. Available tools: {', '.join(self.tool_names())}",
            })

        conn = self.manager.connections[server]
        log.info("Tool: %s (server: %s)", tool_name, server)
        log.info("Arguments: %s", json.dumps(arguments, default=str))

        if not conn.available or conn.session is None:
            log.error("Server '%s' unavailable: %s", server, conn.error)
            return _done({
                "success": False,
                "tool": tool_name,
                "server": server,
                "arguments": arguments,
                "error": f"MCP server '{server}' is unavailable. Please check that the server process can start.",
            })

        try:
            result = await conn.session.call_tool(tool_name, arguments)
            text = _extract_text(result)
            # mcp 2.x uses is_error, mcp 1.x used isError
            is_error = bool(getattr(result, "is_error", None) or getattr(result, "isError", False))
        except Exception as e:
            log.error("Tool execution failed: %s", e)
            return _done({
                "success": False,
                "tool": tool_name,
                "server": server,
                "arguments": arguments,
                "error": f"Tool execution failed: {e}",
            })

        execution_time = time.perf_counter() - start
        if is_error:
            log.error("Response: %s", text)
            log.info("Execution Time: %.4f sec", execution_time)
            return _done({
                "success": False,
                "tool": tool_name,
                "server": server,
                "arguments": arguments,
                "error": text,
            })

        log.info("Response: %s", text if len(text) < 2000 else text[:2000] + " ...[truncated]")
        log.info("Execution Time: %.4f sec", execution_time)
        return _done({
            "success": True,
            "tool": tool_name,
            "server": server,
            "arguments": arguments,
            "response": text,
        })


def _extract_text(result) -> str:
    """Flatten an MCP CallToolResult into a plain string."""
    parts = []
    for block in getattr(result, "content", []) or []:
        text = getattr(block, "text", None)
        parts.append(text if text is not None else str(block))
    return "\n".join(parts).strip() or "(no output)"
