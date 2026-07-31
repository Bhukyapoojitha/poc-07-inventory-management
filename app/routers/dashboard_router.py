from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Product,
    PurchaseOrder,
    StockAlert,
    StockLevel
)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)


@router.get("")
def dashboard(
    db: Session = Depends(get_db)
):
    total_stock_value = 0

    products = db.query(Product).all()

    for product in products:

        stock = (
            db.query(StockLevel)
            .filter(
                StockLevel.product_id == product.id
            )
            .first()
        )

        if stock:
            total_stock_value += (
                stock.quantity_on_hand *
                product.cost_price
            )

    return {
        "total_products":
            db.query(Product).count(),

        "low_stock_count":
            db.query(StockAlert)
            .filter(
                StockAlert.alert_type == "low_stock",
                StockAlert.is_resolved == False
            )
            .count(),

        "out_of_stock_count":
            db.query(StockAlert)
            .filter(
                StockAlert.alert_type == "out_of_stock",
                StockAlert.is_resolved == False
            )
            .count(),

        "open_po_count":
            db.query(PurchaseOrder)
            .filter(
                PurchaseOrder.status != "received"
            )
            .count(),

        "total_stock_value":
            total_stock_value
    }