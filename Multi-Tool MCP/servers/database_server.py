"""PostgreSQL MCP Server (stdio transport).

Tools: customer_details, customer_count, search_product, customer_orders, sales_summary

Connection settings are read from environment variables (see .env):
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_CONNECT_TIMEOUT
"""

import json
import os
from datetime import date

import psycopg
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

mcp = MCPServer("postgresql")


def _conn() -> psycopg.Connection:
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "mcp_shop"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        connect_timeout=int(os.environ.get("DB_CONNECT_TIMEOUT", "5")),
    )


def _query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a query and return rows as dicts. Raises a friendly error on failure."""
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description is None:
                    return []
                cols = [d.name for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
    except psycopg.OperationalError as e:
        raise ToolError(
            "Database connection failed. Please check whether PostgreSQL is running "
            f"and DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD in .env are correct. ({e})"
        ) from e
    except psycopg.Error as e:
        raise ToolError(f"Database query failed: {e}") from e


def _rows(rows: list[dict], empty_msg: str) -> str:
    if not rows:
        return empty_msg
    return json.dumps(rows, indent=2, default=str)


@mcp.tool()
def customer_details(customer_id: int) -> str:
    """Get full details (name, email, city, join date, order count) for one customer by ID."""
    rows = _query(
        """
        SELECT c.id, c.name, c.email, c.city, c.created_at,
               COUNT(o.id) AS total_orders
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.id
        WHERE c.id = %s
        GROUP BY c.id
        """,
        (customer_id,),
    )
    return _rows(rows, f"Customer {customer_id} not found.")


@mcp.tool()
def customer_count() -> str:
    """Get the total number of customers in the database."""
    rows = _query("SELECT COUNT(*) AS customer_count FROM customers")
    return _rows(rows, "No customers found.")


@mcp.tool()
def search_product(query: str) -> str:
    """Search products by name, SKU or description (case-insensitive partial match).

    Args:
        query: Text to search for, e.g. "ABC".
    """
    rows = _query(
        """
        SELECT id, sku, name, price, stock
        FROM products
        WHERE name ILIKE %s OR sku ILIKE %s OR COALESCE(description, '') ILIKE %s
        ORDER BY name
        LIMIT 20
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    )
    return _rows(rows, f"No products matched query '{query}'.")


@mcp.tool()
def customer_orders(customer_id: int) -> str:
    """List all orders for a customer, with the items inside each order."""
    orders = _query(
        """
        SELECT id, order_date, status, total_amount
        FROM orders
        WHERE customer_id = %s
        ORDER BY order_date DESC
        """,
        (customer_id,),
    )
    if not orders:
        return f"No orders found for customer {customer_id}."

    items = _query(
        """
        SELECT oi.order_id, p.name AS product, oi.quantity, oi.unit_price
        FROM order_items oi
        JOIN orders o ON o.id = oi.order_id
        JOIN products p ON p.id = oi.product_id
        WHERE o.customer_id = %s
        ORDER BY oi.order_id
        """,
        (customer_id,),
    )
    items_by_order: dict[int, list] = {}
    for it in items:
        items_by_order.setdefault(it["order_id"], []).append(
            {k: v for k, v in it.items() if k != "order_id"}
        )
    for o in orders:
        o["items"] = items_by_order.get(o["id"], [])

    return json.dumps(orders, indent=2, default=str)


@mcp.tool()
def sales_summary(start_date: str | None = None, end_date: str | None = None) -> str:
    """Aggregate sales summary (orders, revenue, units sold), optionally for a date range.

    Args:
        start_date: Optional inclusive start date in YYYY-MM-DD format.
        end_date: Optional inclusive end date in YYYY-MM-DD format.
    """
    try:
        if start_date:
            date.fromisoformat(start_date)  # validates format, raises ValueError if bad
        if end_date:
            date.fromisoformat(end_date)
    except ValueError as e:
        raise ToolError(f"Invalid date format: {e}. Use YYYY-MM-DD, e.g. 2026-01-15.") from e

    rows = _query(
        """
        SELECT COUNT(DISTINCT o.id)                          AS total_orders,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_revenue,
               COALESCE(SUM(oi.quantity), 0)                 AS units_sold
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.id
        WHERE (%s::date IS NULL OR o.order_date >= %s::date)
          AND (%s::date IS NULL OR o.order_date <= %s::date)
        """,
        (start_date, start_date, end_date, end_date),
    )
    scope = []
    if start_date:
        scope.append(f"from {start_date}")
    if end_date:
        scope.append(f"until {end_date}")
    header = "Sales summary " + (" ".join(scope) if scope else "(all time)") + ":"
    return header + "\n" + _rows(rows, "No sales data available.")


if __name__ == "__main__":
    mcp.run(transport="stdio")
