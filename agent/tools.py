import requests
import structlog

from langchain.tools import tool
from opentelemetry import trace

logger = structlog.get_logger()

tracer = trace.get_tracer("poc-07-agent")

BASE_URL = "http://localhost:8000/api/v1"


def _api_get(
    path: str,
    params: dict = None
) -> dict:
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            params=params or {},
            timeout=10
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        return {
            "error": "API unavailable"
        }

    except requests.exceptions.HTTPError as exc:

        if exc.response.status_code == 404:
            return {
                "error": "not_found"
            }

        return {
            "error": str(exc)
        }

    except Exception as exc:
        return {
            "error": str(exc)
        }


@tool("get_low_stock_alerts")
def get_low_stock_alerts(
    query: str = ""
) -> str:
    """
    Use when asked about low stock products,
    reorder alerts, inventory alerts,
    or out of stock items.
    """

    with tracer.start_as_current_span(
        "tool.get_low_stock_alerts"
    ):
        data = _api_get("/stock/low-alerts")

        if "error" in data:
            return f"Error: {data['error']}"

        if not data:
            return (
                "No low stock alerts. "
                "All products are above reorder points."
            )

        lines = []

        for item in data[:20]:
            lines.append(
                f"- {item.get('id')}: "
                f"{item.get('message')}"
            )

        logger.info(
            "tool_called",
            tool="get_low_stock_alerts"
        )

        return "\n".join(lines)


@tool("get_product_stock")
def get_product_stock(
    product_id: str
) -> str:
    """
    Use when asked about product stock,
    quantity available, inventory levels,
    or product availability.
    """

    with tracer.start_as_current_span(
        "tool.get_product_stock"
    ):
        data = _api_get(
            f"/products/{product_id}"
        )

        if "error" in data:
            return f"Product {product_id} not found."

        stock = data.get(
            "stock_level",
            {}
        )

        return (
            f"Product: {data.get('sku')} - "
            f"{data.get('name')}\n"
            f"On Hand: "
            f"{stock.get('quantity_on_hand', 0)}\n"
            f"Available: "
            f"{stock.get('quantity_available', 0)}\n"
            f"Reserved: "
            f"{stock.get('quantity_reserved', 0)}"
        )


@tool("get_supplier_catalog")
def get_supplier_catalog(
    supplier_id: str
) -> str:
    """
    Use when asked about products provided
    by a supplier, supplier catalog,
    or supplier inventory information.
    """

    with tracer.start_as_current_span(
        "tool.get_supplier_catalog"
    ):
        data = _api_get(
            f"/suppliers/{supplier_id}/catalog"
        )

        if "error" in data:
            return (
                f"Supplier {supplier_id} "
                "catalog unavailable."
            )

        if not data:
            return (
                f"Supplier {supplier_id} "
                "has no products."
            )

        return "\n".join(
            [
                f"{p.get('sku')} - {p.get('name')}"
                for p in data
            ]
        )


@tool("get_dashboard_stats")
def get_dashboard_stats(
    query: str = ""
) -> str:
    """
    Use when asked for inventory dashboard,
    total inventory value, product counts,
    low stock counts, or open purchase orders.
    """

    with tracer.start_as_current_span(
        "tool.get_dashboard_stats"
    ):
        data = _api_get("/dashboard")

        if "error" in data:
            return (
                f"Dashboard unavailable: "
                f"{data['error']}"
            )

        return (
            f"Inventory Dashboard\n"
            f"Total Products: "
            f"{data.get('total_products', 0)}\n"
            f"Low Stock: "
            f"{data.get('low_stock_count', 0)}\n"
            f"Out Of Stock: "
            f"{data.get('out_of_stock_count', 0)}\n"
            f"Open PO: "
            f"{data.get('open_po_count', 0)}\n"
            f"Stock Value: "
            f"{data.get('total_stock_value', 0)}"
        )


@tool("search_inventory_policy")
def search_inventory_policy(
    question: str
) -> str:
    """
    Use when asked about inventory policies,
    reorder calculations, purchase order rules,
    stock movement procedures, or operations.
    """

    try:
        from rag.rag_chain import (
            ask_question,
            build_rag_chain
        )

        result = ask_question(
            question,
            build_rag_chain()
        )

        return result.get(
            "answer",
            "No answer found."
        )

    except Exception as exc:
        return (
            f"Policy search error: {str(exc)}"
        )