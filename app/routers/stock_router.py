from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StockAlert

router = APIRouter(
    prefix="/api/v1/stock",
    tags=["Stock"]
)


@router.get("/low-alerts")
def low_alerts(
    db: Session = Depends(get_db)
):
    alerts = (
        db.query(StockAlert)
        .filter(
            StockAlert.is_resolved == False
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