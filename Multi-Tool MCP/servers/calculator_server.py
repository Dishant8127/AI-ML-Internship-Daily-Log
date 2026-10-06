"""Calculator MCP Server (stdio transport).

Tools: add, subtract, multiply, divide
"""

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("calculator")


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers: add(a, b) -> a + b"""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers: subtract(a, b) -> a - b"""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers: multiply(a, b) -> a * b"""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers: divide(a, b) -> a / b. Fails with a clear error if b == 0."""
    if b == 0:
        raise ToolError("Cannot divide by zero: the second argument is 0.")
    return a / b


if __name__ == "__main__":
    mcp.run(transport="stdio")
