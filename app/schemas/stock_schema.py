from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    message: str