"""Entry point of the Multi-Tool MCP AI Assistant.

Usage:
    python -m assistant.main                      # interactive chat
    python -m assistant.main "What is 125 + 875?"  # single query
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from .llm_agent import LLMAgent
from .logger import setup_logger
from .mcp_client import MCPManager, PROJECT_ROOT
from .tool_manager import ToolManager

SERVERS = {
    "calculator": PROJECT_ROOT / "servers" / "calculator_server.py",
    "filesystem": PROJECT_ROOT / "servers" / "filesystem_server.py",
    "postgresql": PROJECT_ROOT / "servers" / "database_server.py",
}

BANNER = """
============================================================
  Multi-Tool MCP AI Assistant  (Calculator | Files | PostgreSQL)
  type 'exit' or 'quit' to leave
============================================================
"""


async def handle_query(query: str, tools: ToolManager, agent: LLMAgent, logger) -> None:
    print(f"\nyou> {query}")
    started = asyncio.get_event_loop().time()
    answer = await agent.run(query, tools)
    elapsed = asyncio.get_event_loop().time() - started
    print(f"\nassistant> {answer}")
    logger.info("Query round-trip time: %.4f sec\n", elapsed)


async def amain() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    logger = setup_logger()
    logger.info("===== Assistant starting =====")

    manager = MCPManager(SERVERS)
    await manager.start()

    try:
        tools = ToolManager(manager)
        await tools.refresh()

        print(BANNER)
        print("MCP servers:")
        print(manager.summary())
        print(f"\nRegistered tools ({len(tools.tool_names())}): {', '.join(tools.tool_names())}\n")

        if not tools.tool_names():
            print("No MCP tools available - check the server logs above.")
            return 1

        try:
            agent = LLMAgent.from_env()
        except RuntimeError as e:
            logger.error(str(e))
            print(f"ERROR: {e}")
            return 1

        # Single-shot mode: python -m assistant.main "some query"
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:]).strip()
            await handle_query(query, tools, agent, logger)
            return 0

        # Interactive mode
        while True:
            try:
                query = input("you> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nbye!")
                break
            if not query:
                continue
            if query.lower() in {"exit", "quit", "q"}:
                print("bye!")
                break
            try:
                await handle_query(query, tools, agent, logger)
            except KeyboardInterrupt:
                print("\n(interrupted)")
            except Exception as e:  # keep the chat alive on unexpected errors
                logger.error("Unhandled error: %s", e)
                print(f"\nassistant> Sorry, something went wrong: {e}")
        return 0
    finally:
        await manager.stop()
        logger.info("===== Assistant stopped =====")


def main() -> None:
    try:
        raise SystemExit(asyncio.run(amain()))
    except KeyboardInterrupt:
        print("\nbye!")


if __name__ == "__main__":
    main()
