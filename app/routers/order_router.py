from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    PurchaseOrder,
    POItem,
    StockLevel,
    StockMovement
)
from app.schemas.order_schema import PurchaseOrderCreate
from app.services.inventory_service import generate_po_number

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"]
)

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", status_code=201)
def create_order(
    payload: PurchaseOrderCreate,
    db: DbSession
):
    po = PurchaseOrder(
        po_number=generate_po_number(db),
        supplier_id=payload.supplier_id,
        status="draft",
        order_date=datetime.strptime(
            payload.order_date,
            "%Y-%m-%d"
        ).date(),
        expected_delivery=datetime.strptime(
            payload.expected_delivery,
            "%Y-%m-%d"
        ).date()
    )

    db.add(po)
    db.commit()
    db.refresh(po)

    total = 0

    for item in payload.items:
        total += (
            item.quantity_ordered *
            item.unit_cost
        )

        po_item = POItem(
            po_id=po.id,
            product_id=item.product_id,
            quantity_ordered=item.quantity_ordered,
            unit_cost=item.unit_cost,
            quantity_received=0
        )

        db.add(po_item)

    po.total_amount = total

    db.commit()

    return {
        "id": po.id,
        "po_number": po.po_number,
        "status": po.status
    }


@router.get("")
def get_orders(
    db: DbSession
):
    return db.query(
        PurchaseOrder
    ).all()


@router.get(
    "/{order_id}",
    responses={
        404: {
            "description": "Purchase Order not found"
        }
    }
)
def get_order(
    order_id: int,
    db: DbSession
):
    po = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == order_id
        )
        .first()
    )

    if not po:
        raise HTTPException(
            status_code=404,
            detail="Purchase Order not found"
        )

    return po


@router.patch(
    "/{order_id}/receive",
    responses={
        404: {
            "description": "Purchase Order not found"
        }
    }
)
def receive_order(
    order_id: int,
    db: DbSession
):
    po = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.id == order_id
        )
        .first()
    )

    if not po:
        raise HTTPException(
            status_code=404,
            detail="Purchase Order not found"
        )

    for item in po.items:

        stock = (
            db.query(StockLevel)
            .filter(
                StockLevel.product_id ==
                item.product_id
            )
            .first()
        )

        if stock:
            stock.quantity_on_hand += (
                item.quantity_ordered
            )

            movement = StockMovement(
                product_id=item.product_id,
                movement_type="receipt",
                quantity=item.quantity_ordered,
                reference_number=po.po_number,
                notes="PO Receipt"
            )

            db.add(movement)

            item.quantity_received = (
                item.quantity_ordered
            )

    po.status = "received"

    db.commit()

    return {
        "message": "PO Received Successfully",
        "po_number": po.po_number,
        "status": po.status
    }