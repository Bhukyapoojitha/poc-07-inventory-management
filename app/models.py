from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Boolean,
    Date,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    supplier_code = Column(String(20), unique=True)

    products = relationship(
        "Product",
        back_populates="supplier"
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    sku = Column(
        String(20),
        unique=True,
        nullable=False
    )

    name = Column(
        String(200),
        nullable=False
    )

    category = Column(
        String(50),
        nullable=False
    )

    unit_price = Column(Float, nullable=False)

    cost_price = Column(Float, nullable=False)

    reorder_point = Column(
        Integer,
        default=10
    )

    reorder_quantity = Column(
        Integer,
        default=50
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    supplier = relationship(
        "Supplier",
        back_populates="products"
    )

    stock_level = relationship(
        "StockLevel",
        back_populates="product",
        uselist=False
    )

    movements = relationship(
        "StockMovement",
        back_populates="product"
    )

    alerts = relationship(
        "StockAlert",
        back_populates="product"
    )


class StockLevel(Base):
    __tablename__ = "stock_levels"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        unique=True
    )

    quantity_on_hand = Column(
        Integer,
        default=0
    )

    quantity_reserved = Column(
        Integer,
        default=0
    )

    product = relationship(
        "Product",
        back_populates="stock_level"
    )

    @property
    def quantity_available(self):
        return max(
            0,
            self.quantity_on_hand -
            self.quantity_reserved
        )


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    movement_type = Column(
        String(50),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    reference_number = Column(
        String(50),
        nullable=True
    )

    notes = Column(
        String(500),
        nullable=True
    )

    recorded_at = Column(
        DateTime,
        server_default=func.now()
    )

    recorded_by = Column(
        String(100),
        default="system"
    )

    product = relationship(
        "Product",
        back_populates="movements"
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True)

    po_number = Column(
        String(20),
        unique=True,
        nullable=False
    )

    supplier_id = Column(
        Integer,
        ForeignKey("suppliers.id")
    )

    status = Column(
        String(50),
        default="draft"
    )

    total_amount = Column(
        Float,
        default=0.0
    )

    order_date = Column(
        Date,
        nullable=True
    )

    expected_delivery = Column(
        Date,
        nullable=True
    )

    received_date = Column(
        Date,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    items = relationship(
        "POItem",
        back_populates="purchase_order"
    )


class POItem(Base):
    __tablename__ = "po_items"

    id = Column(Integer, primary_key=True)

    po_id = Column(
        Integer,
        ForeignKey("purchase_orders.id")
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    quantity_ordered = Column(
        Integer,
        nullable=False
    )

    unit_cost = Column(
        Float,
        nullable=False
    )

    quantity_received = Column(
        Integer,
        nullable=True
    )

    purchase_order = relationship(
        "PurchaseOrder",
        back_populates="items"
    )


class StockAlert(Base):
    __tablename__ = "stock_alerts"

    id = Column(Integer, primary_key=True)

    product_id = Column(
        Integer,
        ForeignKey("products.id")
    )

    alert_type = Column(
        String(50),
        nullable=False
    )

    message = Column(
        String(500)
    )

    is_resolved = Column(
        Boolean,
        default=False
    )

    triggered_at = Column(
        DateTime,
        server_default=func.now()
    )

    product = relationship(
        "Product",
        back_populates="alerts"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(
        String(200),
        unique=True
    )

    hashed_password = Column(
        String(200)
    )

    full_name = Column(
        String(100)
    )

    role = Column(
        String(50),
        default="staff"
    )

    is_active = Column(
        Boolean,
        default=True
    )