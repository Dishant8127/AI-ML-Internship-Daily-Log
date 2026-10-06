from datetime import datetime, timedelta

from database import (
    Base,
    engine,
    SessionLocal,
    Customer,
    Product,
    Order,
)


def seed_database():

    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:

        existing_customer = db.query(Customer).first()

        if existing_customer:
            print("Database already contains data.")
            return

        # -------------------------
        # Customers
        # -------------------------

        customers = [
            Customer(
                name="Rahul Patel",
                email="rahul@gmail.com",
                phone="9876543210",
                city="Ahmedabad",
            ),
            Customer(
                name="Amit Shah",
                email="amit@gmail.com",
                phone="9876543211",
                city="Surat",
            ),
            Customer(
                name="Priya Mehta",
                email="priya@gmail.com",
                phone="9876543212",
                city="Vadodara",
            ),
            Customer(
                name="Neha Desai",
                email="neha@gmail.com",
                phone="9876543213",
                city="Rajkot",
            ),
            Customer(
                name="Karan Joshi",
                email="karan@gmail.com",
                phone="9876543214",
                city="Ahmedabad",
            ),
        ]

        db.add_all(customers)
        db.commit()

        # -------------------------
        # Products
        # -------------------------

        products = [
            Product(
                name="Floor Cleaner",
                category="Cleaning",
                price=250,
                stock=100,
            ),
            Product(
                name="Glass Cleaner",
                category="Cleaning",
                price=180,
                stock=75,
            ),
            Product(
                name="Toilet Cleaner",
                category="Cleaning",
                price=220,
                stock=60,
            ),
            Product(
                name="Dish Wash Liquid",
                category="Kitchen",
                price=150,
                stock=120,
            ),
            Product(
                name="Garbage Bags",
                category="Cleaning",
                price=100,
                stock=200,
            ),
            Product(
                name="Hand Wash",
                category="Personal Care",
                price=130,
                stock=90,
            ),
            Product(
                name="Disinfectant",
                category="Cleaning",
                price=300,
                stock=50,
            ),
            Product(
                name="Bathroom Cleaner",
                category="Cleaning",
                price=275,
                stock=80,
            ),
        ]

        db.add_all(products)
        db.commit()

        # -------------------------
        # Orders
        # -------------------------

        orders = [
            Order(
                customer_id=1,
                product_id=1,
                quantity=5,
                total_amount=1250,
                order_date=datetime.utcnow() - timedelta(days=2),
                status="Delivered",
            ),
            Order(
                customer_id=1,
                product_id=2,
                quantity=3,
                total_amount=540,
                order_date=datetime.utcnow() - timedelta(days=5),
                status="Delivered",
            ),
            Order(
                customer_id=2,
                product_id=3,
                quantity=4,
                total_amount=880,
                order_date=datetime.utcnow() - timedelta(days=4),
                status="Processing",
            ),
            Order(
                customer_id=2,
                product_id=5,
                quantity=10,
                total_amount=1000,
                order_date=datetime.utcnow() - timedelta(days=7),
                status="Delivered",
            ),
            Order(
                customer_id=3,
                product_id=4,
                quantity=6,
                total_amount=900,
                order_date=datetime.utcnow() - timedelta(days=3),
                status="Delivered",
            ),
            Order(
                customer_id=3,
                product_id=7,
                quantity=2,
                total_amount=600,
                order_date=datetime.utcnow() - timedelta(days=1),
                status="Pending",
            ),
            Order(
                customer_id=4,
                product_id=8,
                quantity=3,
                total_amount=825,
                order_date=datetime.utcnow() - timedelta(days=10),
                status="Delivered",
            ),
            Order(
                customer_id=5,
                product_id=6,
                quantity=8,
                total_amount=1040,
                order_date=datetime.utcnow() - timedelta(days=6),
                status="Delivered",
            ),
        ]

        db.add_all(orders)
        db.commit()

        print("Database seeded successfully.")

    except Exception as e:

        db.rollback()

        print("Error while seeding database:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    seed_database()