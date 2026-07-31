from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    supplier_code: str
