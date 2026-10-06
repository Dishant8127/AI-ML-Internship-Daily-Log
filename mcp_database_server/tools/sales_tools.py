from datetime import datetime

from sqlalchemy import func

from database import SessionLocal, Order


def get_sales_summary(
    start_date: str,
    end_date: str
):

    try:

        start = datetime.strptime(
            start_date,
            "%Y-%m-%d"
        )

        end = datetime.strptime(
            end_date,
            "%Y-%m-%d"
        )

    except ValueError:

        raise ValueError(
            "Dates must use YYYY-MM-DD format."
        )

    if start > end:
        raise ValueError(
            "start_date cannot be greater than end_date."
        )

    # Include the entire end date
    end = end.replace(
        hour=23,
        minute=59,
        second=59
    )

    db = SessionLocal()

    try:

        result = (
            db.query(
                func.count(Order.id),
                func.coalesce(
                    func.sum(Order.quantity),
                    0
                ),
                func.coalesce(
                    func.sum(Order.total_amount),
                    0
                ),
            )
            .filter(
                Order.order_date >= start,
                Order.order_date <= end
            )
            .first()
        )

        total_orders = result[0]
        total_products = result[1]
        total_revenue = result[2]

        return {
            "success": True,
            "start_date": start_date,
            "end_date": end_date,
            "total_orders": total_orders,
            "total_products_sold": total_products,
            "total_revenue": float(total_revenue),
        }

    finally:

        db.close()