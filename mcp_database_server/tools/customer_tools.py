from database import SessionLocal, Customer, Order, Product


def get_customer_details(customer_id: int):

    if customer_id <= 0:
        raise ValueError("customer_id must be greater than 0")

    db = SessionLocal()

    try:

        customer = (
            db.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

        if not customer:
            return {
                "success": False,
                "message": f"Customer {customer_id} was not found."
            }

        return {
            "success": True,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "city": customer.city,
                "created_at": (
                    customer.created_at.isoformat()
                    if customer.created_at
                    else None
                ),
            }
        }

    finally:
        db.close()


def get_customer_orders(customer_id: int):

    if customer_id <= 0:
        raise ValueError("customer_id must be greater than 0")

    db = SessionLocal()

    try:

        customer = (
            db.query(Customer)
            .filter(Customer.id == customer_id)
            .first()
        )

        if not customer:
            return {
                "success": False,
                "message": f"Customer {customer_id} was not found."
            }

        orders = (
            db.query(Order, Product)
            .join(Product, Order.product_id == Product.id)
            .filter(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .all()
        )

        result = []

        for order, product in orders:

            result.append({
                "order_id": order.id,
                "product": product.name,
                "quantity": order.quantity,
                "total_amount": order.total_amount,
                "order_date": order.order_date.isoformat(),
                "status": order.status,
            })

        return {
            "success": True,
            "customer_id": customer_id,
            "customer_name": customer.name,
            "orders": result,
            "total_orders": len(result),
        }

    finally:
        db.close()