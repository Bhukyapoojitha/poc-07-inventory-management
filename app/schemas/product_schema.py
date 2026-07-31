from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category: str
    unit_price: float
    cost_price: float
    reorder_point: int = 10
    reorder_quantity: int = 50
    supplier_id: int | None = None


class StockUpdate(BaseModel):
    movement_type: str
    quantity: int
    reference_number: str | None = None
    notes: str | None = None