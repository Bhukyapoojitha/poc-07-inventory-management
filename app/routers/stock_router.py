from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StockAlert

router = APIRouter(
    prefix="/api/v1/stock",
    tags=["Stock"]
)

DbSession = Annotated[Session, Depends(get_db)]


@router.get("/low-alerts")
def low_alerts(
    db: DbSession
):
    alerts = (
        db.query(StockAlert)
        .filter(
            StockAlert.is_resolved.is_(False)
        )
        .all()
    )

    return [
        {
            "id": alert.product_id,
            "alert_type": alert.alert_type,
            "message": alert.message
        }
        for alert in alerts
    ]