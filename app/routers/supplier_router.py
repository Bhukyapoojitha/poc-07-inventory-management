from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(
    prefix="/api/v1/suppliers",
    tags=["Suppliers"]
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{supplier_id}/catalog")
def supplier_catalog(
    supplier_id: int,
    db: DbSession
):
    products = (
        db.query(Product)
        .filter(
            Product.supplier_id == supplier_id
        )
        .all()
    )

    return products