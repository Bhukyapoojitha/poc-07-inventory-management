import structlog

from typing import Dict
from typing import List

from langsmith import traceable

from langchain_core.tools import StructuredTool

from mcp_server.mcp_app import (
    update_stock,
    create_purchase_order,
    get_low_stock_products,
    get_supplier_catalog,
    get_purchase_orders,
    get_inventory_dashboard
)

logger = structlog.get_logger()


class ChatSession:

    def __init__(
        self,
        session_id: str
    ):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []

    def add_message(
        self,
        role: str,
        content: str
    ):
        self.history.append(
            {
                "role": role,
                "content": content
            }
        )

    def get_history_for_llm(self):
        return self.history[-10:]


class MCPExecutor:

    def __init__(self, tools):
        self.tools = tools

    def invoke(self, payload):

        message = payload.get(
            "input",
            ""
        ).lower()

        if "dashboard" in message:
            return {
                "output": str(
                    get_inventory_dashboard()
                )
            }

        if (
            "low stock" in message
            or "reorder" in message
        ):
            return {
                "output": str(
                    get_low_stock_products()
                )
            }

        if (
            "purchase order" in message
            or "orders" in message
        ):
            return {
                "output": str(
                    get_purchase_orders()
                )
            }

        if "supplier" in message:
            return {
                "output": str(
                    get_supplier_catalog(1)
                )
            }

        return {
            "output":
            (
                "Available commands:\n\n"
                "• Show inventory dashboard\n"
                "• Show low stock products\n"
                "• Show purchase orders\n"
                "• Show supplier catalog"
            )
        }


def build_chat_executor():

    tools = [
        StructuredTool.from_function(
            update_stock,
            description="Record stock movement for a product"
        ),
        StructuredTool.from_function(
            create_purchase_order,
            description="Create purchase order"
        ),
        StructuredTool.from_function(
            get_low_stock_products,
            description="Get low stock products"
        ),
        StructuredTool.from_function(
            get_supplier_catalog,
            description="Supplier catalog"
        ),
        StructuredTool.from_function(
            get_purchase_orders,
            description="Purchase order list"
        ),
        StructuredTool.from_function(
            get_inventory_dashboard,
            description="Inventory dashboard metrics"
        )
    ]

    return MCPExecutor(tools)


@traceable(
    project_name="AI-Readiness-POC-07-P4"
)
def process_message(
    message: str,
    session_id: str = "default"
):

    try:

        logger.info(
            "chat_message",
            poc_id="POC-07",
            phase="P4",
            session_id=session_id,
            message=message
        )

        executor = build_chat_executor()

        result = executor.invoke(
            {
                "input": message
            }
        )

        return {
            "output":
            result.get(
                "output",
                ""
            ),
            "session_id":
            session_id
        }

    except Exception as exc:

        logger.error(
            "chat_error",
            poc_id="POC-07",
            phase="P4",
            error=str(exc)
        )

        return {
            "output":
            f"Error: {str(exc)}",
            "session_id":
            session_id
        }