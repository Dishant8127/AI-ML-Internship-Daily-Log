import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from llm_client import ask_nvidia


SERVER_PATH = os.path.abspath("server.py")


async def run_chat():

    server_params = StdioServerParameters(
        command="python",
        args=[SERVER_PATH],
        env=os.environ.copy(),
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("\nMCP Server connected successfully.")

            # Get MCP tools
            tools_result = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools_result.tools:
                print(f"- {tool.name}")

            # Convert MCP tools to NVIDIA/OpenAI format
            llm_tools = []

            for tool in tools_result.tools:

                llm_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema,
                    }
                })

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a database assistant. "
                        "Use the available MCP tools to answer "
                        "customer, product, order and sales questions. "
                        "Do not invent database information."
                    )
                }
            ]

            print("\nType 'exit' to quit.")

            while True:

                user_input = input("\nYou: ").strip()

                if user_input.lower() == "exit":
                    break

                if not user_input:
                    continue

                messages.append({
                    "role": "user",
                    "content": user_input
                })

                # First LLM call
                response = ask_nvidia(
                    messages,
                    llm_tools
                )

                assistant_message = response.choices[0].message

                # Add assistant response
                messages.append(
                    assistant_message.model_dump()
                )

                # Check if LLM selected a tool
                if assistant_message.tool_calls:

                    for tool_call in assistant_message.tool_calls:

                        tool_name = tool_call.function.name

                        arguments = json.loads(
                            tool_call.function.arguments
                        )

                        print(
                            f"\nLLM selected tool: {tool_name}"
                        )

                        print(
                            f"Arguments: {arguments}"
                        )

                        # Execute MCP tool
                        result = await session.call_tool(
                            tool_name,
                            arguments=arguments
                        )

                        # Extract result
                        tool_result = []

                        for content in result.content:

                            if hasattr(content, "text"):
                                tool_result.append(
                                    content.text
                                )

                        tool_output = "\n".join(
                            tool_result
                        )

                        print(
                            f"MCP result: {tool_output}"
                        )

                        # Send tool result back to LLM
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_output,
                        })

                    # Second LLM call
                    final_response = ask_nvidia(
                        messages,
                        llm_tools
                    )

                    final_message = (
                        final_response
                        .choices[0]
                        .message
                        .content
                    )

                    print(
                        f"\nAssistant: {final_message}"
                    )

                    messages.append({
                        "role": "assistant",
                        "content": final_message,
                    })

                else:

                    answer = assistant_message.content

                    print(
                        f"\nAssistant: {answer}"
                    )


if __name__ == "__main__":
    asyncio.run(run_chat())