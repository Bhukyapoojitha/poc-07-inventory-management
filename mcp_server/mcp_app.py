import requests
import structlog

from fastmcp import FastMCP
from opentelemetry import trace

logger = structlog.get_logger()

tracer = trace.get_tracer("poc-07-mcp")

BASE_URL = "http://localhost:8000/api/v1"

mcp = FastMCP("Inventory Management Server")


def _get(path, params=None):
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            params=params or {},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        return {"error": "API unavailable"}

    except Exception as exc:
        return {"error": str(exc)}


def _post(path, payload):
    try:
        response = requests.post(
            f"{BASE_URL}{path}",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        return {"error": "API unavailable"}

    except Exception as exc:
        return {"error": str(exc)}


@mcp.tool()
def update_stock(
    product_id: int,
    movement_type: str,
    quantity: int,
    reference_number: str = None,
    notes: str = None
) -> dict:

    with tracer.start_as_current_span(
        "mcp.tool.update_stock"
    ):
        payload = {
            "movement_type": movement_type,
            "quantity": quantity,
            "reference_number": reference_number,
            "notes": notes
        }

        logger.info(
            "mcp_tool_called",
            poc_id="POC-07",
            tool="update_stock"
        )

        return _post(
            f"/products/{product_id}/stock",
            payload
        )


@mcp.tool()
def create_purchase_order(
    supplier_id: int,
    order_date: str,
    items: list,
    expected_delivery: str = None
) -> dict:

    with tracer.start_as_current_span(
        "mcp.tool.create_purchase_order"
    ):
        payload = {
            "supplier_id": supplier_id,
            "order_date": order_date,
            "items": items,
            "expected_delivery": expected_delivery
        }

        logger.info(
            "mcp_tool_called",
            poc_id="POC-07",
            tool="create_purchase_order"
        )

        return _post(
            "/orders",
            payload
        )


@mcp.tool()
def get_low_stock_products() -> list:

    with tracer.start_as_current_span(
        "mcp.tool.get_low_stock_products"
    ):
        return _get("/stock/low-alerts")


@mcp.tool()
def get_supplier_catalog(
    supplier_id: int
) -> list:

    with tracer.start_as_current_span(
        "mcp.tool.get_supplier_catalog"
    ):
        return _get(
            f"/suppliers/{supplier_id}/catalog"
        )


@mcp.tool()
def get_purchase_orders(
    status: str = None,
    supplier_id: int = None
) -> list:

    params = {}

    if status:
        params["status"] = status

    if supplier_id:
        params["supplier_id"] = supplier_id

    with tracer.start_as_current_span(
        "mcp.tool.get_purchase_orders"
    ):
        return _get(
            "/orders",
            params
        )


@mcp.tool()
def get_inventory_dashboard() -> dict:

    with tracer.start_as_current_span(
        "mcp.tool.get_inventory_dashboard"
    ):
        return _get("/dashboard")


if __name__ == "__main__":
    mcp.run()