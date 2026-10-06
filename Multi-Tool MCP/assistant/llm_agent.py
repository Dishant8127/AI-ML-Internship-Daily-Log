"""LLM agent: decides which MCP tools to call and builds the final answer.

Uses an NVIDIA NIM endpoint (OpenAI-compatible chat completions).
The model answers with strict JSON actions:

    {"action": "tool", "tool": "...", "arguments": {...}}
    {"action": "final", "answer": "..."}

Each tool result is fed back to the model, which enables multi-step
execution and tool chaining (output of one tool -> input of the next).
"""

import json
import os
import re
import time

from openai import AsyncOpenAI

from .logger import get_logger
from .tool_manager import ToolManager

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"

SYSTEM_PROMPT = """You are an AI assistant connected to multiple MCP servers \
(Calculator, File System, PostgreSQL). You solve the user's request by calling tools.

{tool_list}

How to respond - ALWAYS reply with a single JSON object and nothing else:

To call a tool:
{{"action": "tool", "tool": "<tool name>", "arguments": {{<argument name>: <value>...}}}}

When you have everything needed for the user:
{{"action": "final", "answer": "<concise natural-language answer>"}}

Rules:
1. Select only the tools the request actually needs; never call unnecessary tools.
2. If several tools are required, call them ONE AT A TIME, in the correct order.
3. Use the output of one tool as input to another tool when necessary \
(e.g. take a product price from search_product, then compute with multiply).
4. NEVER invent tool results - only use the TOOL RESULT messages you receive.
5. If a tool fails, do not retry it more than once; explain the error clearly \
in plain language (no raw tracebacks), suggesting what the user should check.
6. All tool arguments must be valid for that tool's declared schema, and the \
"arguments" object must always be present with every required argument - never omit it.
7. Reply with JSON only - no markdown, no commentary outside the JSON object."""


class LLMAgent:
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        max_steps: int = 6,
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_steps = max_steps

    @classmethod
    def from_env(cls) -> "LLMAgent":
        api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
        if not api_key or api_key.startswith("your_"):
            raise RuntimeError(
                "NVIDIA_API_KEY is not set. Put your NVIDIA API key in .env "
                "(NVIDIA_API_KEY=nvapi-...)."
            )
        return cls(
            api_key=api_key,
            base_url=os.environ.get("NVIDIA_BASE_URL", DEFAULT_BASE_URL),
            model=os.environ.get("NVIDIA_MODEL", DEFAULT_MODEL),
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "1024")),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1")),
            max_steps=int(os.environ.get("MAX_TOOL_STEPS", "6")),
        )

    # ------------------------------------------------------------------ LLM I/O
    async def _chat(self, messages: list[dict]) -> str:
        """One chat completion; retries once if the model returns empty content."""
        content = ""
        for attempt in range(2):
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            choice = resp.choices[0]
            content = (choice.message.content or "").strip()
            if content:
                return content
            get_logger().warning(
                "LLM returned empty content (finish_reason=%s), retry %d/2",
                getattr(choice, "finish_reason", None), attempt + 1,
            )
        raise RuntimeError("LLM returned an empty response.")

    @staticmethod
    def _parse_action(content: str) -> dict | None:
        """Extract a JSON action object from the model reply (tolerates fences/prose)."""
        text = content.strip()
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
        candidates = [text]
        first, last = text.find("{"), text.rfind("}")
        if first != -1 and last > first:
            candidates.append(text[first:last + 1])

        decoder = json.JSONDecoder()
        for cand in candidates:
            try:
                obj = json.loads(cand)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and obj.get("action") in ("tool", "final"):
                return obj
            return None

        # last resort: scan for the first decodable object
        idx = text.find("{")
        while idx != -1:
            try:
                obj, _ = decoder.raw_decode(text[idx:])
                if isinstance(obj, dict) and obj.get("action") in ("tool", "final"):
                    return obj
            except json.JSONDecodeError:
                pass
            idx = text.find("{", idx + 1)
        return None

    # ------------------------------------------------------------------- agent
    async def run(self, query: str, tools: ToolManager) -> str:
        """Agentic loop: think -> call tool -> observe -> repeat -> final answer."""
        log = get_logger()
        system = SYSTEM_PROMPT.format(tool_list=tools.describe_tools())
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": query},
        ]
        log.info("Query: %s", query)
        log.info("Available tools: %s", ", ".join(tools.tool_names()))

        parse_failures = 0
        for step in range(1, self.max_steps + 1):
            try:
                content = await self._chat(messages)
            except Exception as e:
                log.error("LLM response error: %s", e)
                return (
                    "I couldn't get a response from the language model right now "
                    f"({e}). Please check your NVIDIA API key and connection."
                )

            action = self._parse_action(content)
            if action is None:
                parse_failures += 1
                log.warning("LLM produced non-JSON output (attempt %d): %s", parse_failures, content[:300])
                if parse_failures >= 3:
                    return (
                        "I had trouble producing a structured plan for this request. "
                        "Please try rephrasing it."
                    )
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": "That was not valid JSON. Reply with ONLY a JSON object: "
                               '{"action":"tool",...} or {"action":"final",...}',
                })
                continue

            messages.append({"role": "assistant", "content": content})
            log.debug("LLM action: %s", content)

            if action["action"] == "final":
                answer = str(action.get("answer", "")).strip() or "(empty answer)"
                log.info("Final response: %s", answer)
                return answer

            # ---- tool call
            tool_name = str(action.get("tool", "")).strip()
            arguments = action.get("arguments")
            if arguments is None:
                # Some models put arguments at the top level of the action object
                # or omit the "arguments" key entirely; recover them if possible.
                arguments = {
                    k: v for k, v in action.items()
                    if k not in {"action", "tool", "answer", "thought", "reason", "reasoning"}
                }
            if not isinstance(arguments, dict):
                arguments = {}
            if not tool_name:
                result = {"success": False, "tool": None, "arguments": arguments,
                          "error": "Missing 'tool' field in the action.", "execution_time": 0.0}
            else:
                result = await tools.execute(tool_name, arguments)

            messages.append({
                "role": "user",
                "content": "TOOL RESULT:\n" + json.dumps(result, indent=2, default=str)
                           + "\n\nContinue. Reply with the next JSON action only.",
            })

        log.warning("Stopped after reaching MAX_TOOL_STEPS=%d", self.max_steps)
        return (
            f"I needed more than {self.max_steps} tool steps to finish this request. "
            "Please split it into a smaller question, or raise MAX_TOOL_STEPS in .env."
        )


def timed(fn):
    """Tiny helper kept for reference: measures coroutine wall time."""

    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        out = await fn(*args, **kwargs)
        get_logger().info("Execution time: %.4f seconds", time.perf_counter() - start)
        return out

    return wrapper
