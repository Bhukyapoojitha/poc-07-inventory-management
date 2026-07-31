from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"]
)


@router.get("/{supplier_id}/catalog")
def supplier_catalog(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    products = (
        db.query(Product)
        .filter(
            Product.supplier_id == supplier_id
        )
        .all()
    )

    return products