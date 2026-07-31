from datetime import date

from app.models import (
    Product,
    PurchaseOrder,
    StockAlert
)

CATEGORY_PREFIXES = {
    "grocery": "GRO",
    "electronics": "ELC",
    "clothing": "CLO",
    "household": "HHD",
    "personal_care": "PRC"
}


def generate_sku(category: str, db):
    prefix = CATEGORY_PREFIXES.get(category, "GEN")

    count = (
        db.query(Product)
        .filter(
            Product.sku.like(f"SKU-{prefix}-%")
        )
        .count()
    )

    return f"SKU-{prefix}-{count + 1:04d}"


def generate_po_number(db):
    year = date.today().year

    count = (
        db.query(PurchaseOrder)
        .filter(
            PurchaseOrder.po_number.like(
                f"PO-{year}-%"
            )
        )
        .count()
    )

    return f"PO-{year}-{count + 1:04d}"


def check_stock_alerts(
    product,
    stock,
    db
):
    available = stock.quantity_available

    if available == 0:

        alert = StockAlert(
            product_id=product.id,
            alert_type="out_of_stock",
            message=f"SKU {product.sku} is OUT OF STOCK."
        )

        db.add(alert)

    elif available <= product.reorder_point:

        alert = StockAlert(
            product_id=product.id,
            alert_type="low_stock",
            message=(
                f"SKU {product.sku}: only "
                f"{available} units left "
                f"(reorder point: "
                f"{product.reorder_point})."
            )
        )

        db.add(alert)