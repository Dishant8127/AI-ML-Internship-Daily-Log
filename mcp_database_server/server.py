# from mcp.server.fastmcp import FastMCP
from mcp.server import MCPServer

from database import create_tables

from tools.customer_tools import (
    get_customer_details,
    get_customer_orders,
)

from tools.product_tools import (
    search_products,
)

from tools.sales_tools import (
    get_sales_summary,
)


# Create tables if they don't exist
create_tables()


mcp = MCPServer(
    "PostgreSQL Database Server"
)


@mcp.tool()
def customer_details(customer_id: int) -> dict:
    """
    Retrieve details of a customer using customer ID.
    """

    return get_customer_details(customer_id)


@mcp.tool()
def search_product(query: str) -> dict:
    """
    Search products by product name or category.
    """

    return search_products(query)


@mcp.tool()
def customer_orders(customer_id: int) -> dict:
    """
    Retrieve all orders placed by a customer.
    """

    return get_customer_orders(customer_id)


@mcp.tool()
def sales_summary(
    start_date: str,
    end_date: str
) -> dict:
    """
    Generate sales summary for a date range.
    """

    return get_sales_summary(
        start_date,
        end_date
    )


if __name__ == "__main__":

    mcp.run()