from sqlalchemy import or_

from database import SessionLocal, Product


def search_products(query: str):

    if not query or not query.strip():
        raise ValueError("Product search query cannot be empty.")

    query = query.strip()

    if len(query) > 100:
        raise ValueError(
            "Product search query cannot exceed 100 characters."
        )

    db = SessionLocal()

    try:

        search_pattern = f"%{query}%"

        products = (
            db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.category.ilike(search_pattern)
                )
            )
            .order_by(Product.name)
            .all()
        )

        result = []

        for product in products:

            result.append({
                "id": product.id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "stock": product.stock,
                "available": product.stock > 0,
            })

        return {
            "success": True,
            "query": query,
            "count": len(result),
            "products": result,
        }

    finally:
        db.close()