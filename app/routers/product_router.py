from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Product,
    StockLevel,
    StockMovement
)

from app.schemas.product_schema import (
    ProductCreate,
    StockUpdate
)

from app.services.inventory_service import (
    generate_sku,
    check_stock_alerts
)

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)


@router.post("", status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    sku = generate_sku(
        product.category,
        db
    )

    new_product = Product(
        sku=sku,
        name=product.name,
        category=product.category,
        unit_price=product.unit_price,
        cost_price=product.cost_price,
        reorder_point=product.reorder_point,
        reorder_quantity=product.reorder_quantity,
        supplier_id=product.supplier_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    stock = StockLevel(
        product_id=new_product.id,
        quantity_on_hand=0,
        quantity_reserved=0
    )

    db.add(stock)
    db.commit()

    return {
        "id": new_product.id,
        "sku": new_product.sku,
        "name": new_product.name
    }


@router.get("")
def get_products(
    category: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    if category:
        query = query.filter(
            Product.category == category
        )

    return query.all()


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    stock = (
        db.query(StockLevel)
        .filter(
            StockLevel.product_id == product_id
        )
        .first()
    )

    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "category": product.category,
        "stock_level": {
            "quantity_on_hand": stock.quantity_on_hand if stock else 0,
            "quantity_reserved": stock.quantity_reserved if stock else 0
        }
    }


@router.patch("/{product_id}/stock")
def update_stock(
    product_id: int,
    stock_update: StockUpdate,
    db: Session = Depends(get_db)
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    stock = (
        db.query(StockLevel)
        .filter(
            StockLevel.product_id == product_id
        )
        .first()
    )

    if not stock:
        raise HTTPException(
            status_code=404,
            detail="Stock not found"
        )

    stock.quantity_on_hand += stock_update.quantity

    movement = StockMovement(
        product_id=product_id,
        movement_type=stock_update.movement_type,
        quantity=stock_update.quantity,
        reference_number=stock_update.reference_number,
        notes=stock_update.notes
    )

    db.add(movement)

    check_stock_alerts(
        product,
        stock,
        db
    )

    db.commit()

    return {
        "message": "Stock Updated"
    }