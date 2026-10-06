# Day 4 - Multi-Tool MCP AI Assistant

An MCP-based AI assistant that connects **multiple MCP servers** (Calculator, File System,
PostgreSQL) to one LLM agent. You ask in natural language; the LLM decides which tools to
call, generates the arguments, executes them (one tool, many tools, or chained tools) and
writes the final natural-language answer.

```text
                         User
                           |
                           v
                  +-----------------+
                  |   AI Assistant  |
                  |   MCP Client    |
                  +--------+--------+
                           |
                +----------+----------+
                |          |          |
                v          v          v
        Calculator      File System   PostgreSQL
        MCP Server      MCP Server    MCP Server
                |          |          |
                v          v          v
           Calculations   Local Files   Database
```

## Project structure

```text
.
├── servers/
│   ├── calculator_server.py     # add, subtract, multiply, divide
│   ├── filesystem_server.py     # list_files, read_file, search_file, file_metadata
│   └── database_server.py       # customer_details, customer_count,
│                                # search_product, customer_orders, sales_summary
├── assistant/
│   ├── mcp_client.py            # persistent stdio connections to all MCP servers
│   ├── tool_manager.py          # common tool registry + executor + timing/logging
│   ├── llm_agent.py             # LLM decision loop (NVIDIA NIM, OpenAI-compatible)
│   ├── logger.py                # file + console logging
│   └── main.py                  # CLI entry point
├── database/
│   └── seed.sql                 # sample customers/products/orders data
├── logs/
│   └── assistant.log            # query / tool / args / response / execution time
├── .env                         # API key + DB credentials (never commit)
├── requirements.txt
└── README.md
```

## Setup

```bash
# 1. virtualenv + dependencies
python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash); use `source .venv/bin/activate` on Linux/macOS
pip install -r requirements.txt

# 2. configure .env
#    NVIDIA_API_KEY=nvapi-...        your NVIDIA NIM key
#    NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
#    DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD

# 3. seed the sample database (creates tables in DB_NAME)
psql -U postgres -d mcp -f database/seed.sql
# (or run database/seed.sql through any SQL client you use)
```

## Run

```bash
# interactive chat
python -m assistant.main

# single query
python -m assistant.main "What is 125 + 875?"
```

## How it works

```text
User Query
    -> MCP AI Assistant starts all 3 MCP servers (stdio) and merges their tools
    -> LLM receives the full tool list (name, description, argument schema)
    -> LLM replies with a JSON action:
         {"action": "tool", "tool": "...", "arguments": {...}}
         {"action": "final", "answer": "..."}
    -> tool executed through the MCP session, result fed back to the LLM
    -> repeat until the LLM can answer (multi-tool + chaining)
    -> final natural-language response
```

Because each tool result goes back into the conversation, the model can chain:

```text
search_product("ABC")  ->  price = 100
multiply(100, 1.18)    ->  118
final answer
```

## Test queries

Single tool:

```text
What is 125 + 875?
List all files in my project.
Show details of customer 5.
```

Multi-tool:

```text
Calculate 250 * 45 and tell me how many customers are in the database.
Calculate 100 / 4 and find all Python files in my project.
```

Tool chaining:

```text
Find the price of product ABC and calculate its price after adding 18% GST.
```

Error handling:

```text
Divide 100 by zero.
Show details of customer 999999.
Read a file that does not exist.
```

## Logging

Every request writes to `logs/assistant.log` and the console:

```text
Query: Calculate 250 * 45
Tool: multiply (server: calculator)
Arguments: {"a": 250, "b": 45}
Response: 11250.0
Execution Time: 0.1000 sec
Final response: ...
```

Set `LOG_LEVEL=DEBUG` in `.env` to also log the raw LLM action JSON.

## Error handling

Failures never crash the assistant and never show raw tracebacks to the user:

| Failure | Behaviour |
|---|---|
| Tool not found | `Tool not found: 'x'. Available tools: ...` fed back to the LLM |
| Invalid/missing arguments | validation error fed back, model corrects itself |
| Division by zero | `Cannot divide by zero` (`ToolError`, `is_error=True`) |
| File/directory not found | `File not found: ...` |
| Database down / bad credentials | friendly "check PostgreSQL and .env" message |
| MCP server process fails to start | server marked DOWN, other servers keep working |
| LLM API error / empty response | clear message, one automatic retry for empty replies |
| More than `MAX_TOOL_STEPS` tools | explains the limit instead of looping forever |

## Configuration (.env)

| Key | Purpose |
|---|---|
| `NVIDIA_API_KEY` | NVIDIA NIM API key |
| `NVIDIA_BASE_URL` | defaults to `https://integrate.api.nvidia.com/v1` |
| `NVIDIA_MODEL` | chat model id |
| `LLM_MAX_TOKENS`, `LLM_TEMPERATURE` | generation settings |
| `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD` | PostgreSQL connection |
| `MAX_TOOL_STEPS` | max tool calls per query (default 6) |
| `LOG_LEVEL` | `INFO` or `DEBUG` |
