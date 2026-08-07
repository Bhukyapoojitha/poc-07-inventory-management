from datetime import date
import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import (
    Product,
    StockLevel,
    StockMovement,
    PurchaseOrder,
    Supplier
)


def test_sku_unique():
    db = SessionLocal()

    sku = f"SKU-GRO-{uuid.uuid4().hex[:8]}"

    product_one = Product(
        sku=sku,
        name="Test 1",
        category="grocery",
        unit_price=100,
        cost_price=80
    )

    db.add(product_one)
    db.commit()

    product_two = Product(
        sku=sku,
        name="Test 2",
        category="grocery",
        unit_price=100,
        cost_price=80
    )

    db.add(product_two)

    with pytest.raises(IntegrityError) as exc_info:
        db.commit()

    assert exc_info.value is not None

    db.rollback()
    db.close()


def test_movement_linked():
    db = SessionLocal()

    product = Product(
        sku=f"SKU-GRO-{uuid.uuid4().hex[:8]}",
        name="Rice",
        category="grocery",
        unit_price=100,
        cost_price=80
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    movement = StockMovement(
        product_id=product.id,
        movement_type="receipt",
        quantity=50,
        recorded_by="Kiran"
    )

    db.add(movement)
    db.commit()

    assert movement.id is not None
    assert movement.product_id == product.id

    db.close()


def test_po_unique():
    db = SessionLocal()

    supplier = Supplier(
        name="ABC Supplier",
        supplier_code=f"SUP-{uuid.uuid4().hex[:6]}"
    )

    db.add(supplier)
    db.commit()
    db.refresh(supplier)

    po_number = f"PO-2026-{uuid.uuid4().hex[:8]}"

    purchase_order_one = PurchaseOrder(
        po_number=po_number,
        supplier_id=supplier.id,
        order_date=date.today()
    )

    db.add(purchase_order_one)
    db.commit()

    purchase_order_two = PurchaseOrder(
        po_number=po_number,
        supplier_id=supplier.id,
        order_date=date.today()
    )

    db.add(purchase_order_two)

    with pytest.raises(IntegrityError) as exc_info:
        db.commit()

    assert exc_info.value is not None

    db.rollback()
    db.close()


def test_stocklevel_one_to_one():
    db = SessionLocal()

    product = Product(
        sku=f"SKU-GRO-{uuid.uuid4().hex[:8]}",
        name="Oil",
        category="grocery",
        unit_price=100,
        cost_price=80
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    stock_level_one = StockLevel(
        product_id=product.id,
        quantity_on_hand=100
    )

    db.add(stock_level_one)
    db.commit()

    stock_level_two = StockLevel(
        product_id=product.id,
        quantity_on_hand=50
    )

    db.add(stock_level_two)

    with pytest.raises(IntegrityError) as exc_info:
        db.commit()

    assert exc_info.value is not None

    db.rollback()
    db.close()