from datetime import datetime

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    phone = Column(String(20))
    city = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship(
        "Order",
        back_populates="customer"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship(
        "Order",
        back_populates="product"
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    quantity = Column(Integer, nullable=False)
    total_amount = Column(Float, nullable=False)

    order_date = Column(
        DateTime,
        default=datetime.utcnow
    )

    status = Column(
        String(50),
        default="Pending"
    )

    customer = relationship(
        "Customer",
        back_populates="orders"
    )

    product = relationship(
        "Product",
        back_populates="orders"
    )


def create_tables():
    Base.metadata.create_all(bind=engine)