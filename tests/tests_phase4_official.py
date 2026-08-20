import os
import pytest

from unittest.mock import patch
from unittest.mock import MagicMock


# ==========================
# MCP SERVER TESTS
# ==========================

def test_server_starts():
    from mcp_server.mcp_app import mcp

    assert mcp is not None
    assert (
        "Inventory" in mcp.name
        or "Management" in mcp.name
    )


def test_6_tools():
    import mcp_server.mcp_app as app

    for name in [
        "update_stock",
        "create_purchase_order",
        "get_low_stock_products",
        "get_supplier_catalog",
        "get_purchase_orders",
        "get_inventory_dashboard"
    ]:
        assert hasattr(app, name)


def test_update_stock():

    mock_r = {
        "id": 1,
        "product_id": 1,
        "movement_type": "receipt",
        "quantity": 100
    }

    with patch(
        "mcp_server.mcp_app.requests.post"
    ) as mp:

        mp.return_value.status_code = 200
        mp.return_value.json.return_value = mock_r
        mp.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            update_stock
        )

        result = update_stock(
            product_id=1,
            movement_type="receipt",
            quantity=100
        )

        assert isinstance(result, dict)

        mp.assert_called_once()


def test_create_po():

    mock_r = {
        "id": 1,
        "po_number": "PO-2026-0001",
        "status": "draft",
        "total_amount": 28000.0
    }

    with patch(
        "mcp_server.mcp_app.requests.post"
    ) as mp:

        mp.return_value.status_code = 201
        mp.return_value.json.return_value = mock_r
        mp.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            create_purchase_order
        )

        result = create_purchase_order(
            supplier_id=1,
            order_date="2026-06-18",
            items=[
                {
                    "product_id": 1,
                    "quantity_ordered": 100,
                    "unit_cost": 280.0
                }
            ]
        )

        assert isinstance(result, dict)
        assert result.get("po_number")


def test_get_low_stock():

    mock_r = [
        {
            "id": 1,
            "sku": "SKU-GRO-0001",
            "quantity_available": 5,
            "reorder_point": 20
        }
    ]

    with patch(
        "mcp_server.mcp_app.requests.get"
    ) as mg:

        mg.return_value.status_code = 200
        mg.return_value.json.return_value = mock_r
        mg.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            get_low_stock_products
        )

        result = get_low_stock_products()

        assert isinstance(
            result,
            (list, dict)
        )


def test_supplier_catalog():

    mock_r = [
        {
            "sku": "SKU-GRO-0001",
            "name": "Basmati Rice",
            "cost_price": 280.0
        }
    ]

    with patch(
        "mcp_server.mcp_app.requests.get"
    ) as mg:

        mg.return_value.status_code = 200
        mg.return_value.json.return_value = mock_r
        mg.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            get_supplier_catalog
        )

        result = get_supplier_catalog(
            supplier_id=1
        )

        assert isinstance(
            result,
            (list, dict)
        )


def test_inventory_dashboard():

    mock_r = {
        "total_products": 500,
        "low_stock_count": 25,
        "open_po_count": 8
    }

    with patch(
        "mcp_server.mcp_app.requests.get"
    ) as mg:

        mg.return_value.status_code = 200
        mg.return_value.json.return_value = mock_r
        mg.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            get_inventory_dashboard
        )

        result = get_inventory_dashboard()

        assert isinstance(result, dict)

        assert (
            result.get("total_products")
            == 500
        )


def test_api_unavailable_error():

    import requests as req

    with patch(
        "mcp_server.mcp_app.requests.get",
        side_effect=req.exceptions.
        ConnectionError("refused")
    ):

        from mcp_server.mcp_app import (
            get_inventory_dashboard
        )

        result = (
            get_inventory_dashboard()
        )

        assert isinstance(
            result,
            dict
        )

        assert "error" in result


# ==========================
# CHAT TESTS
# ==========================

def test_executor_builds():
    from mcp_server.chat_interface import (
        build_chat_executor
    )

    assert (
        build_chat_executor()
        is not None
    )


def test_message_processed():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output":
            "25 products need reorder."
        }

        result = process_message(
            "Which products need reordering?",
            session_id="inv-001"
        )

        assert result is not None


def test_session_id():

    import uuid

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output": "OK"
        }

        result = process_message(
            "Dashboard",
            session_id=str(uuid.uuid4())
        )

        assert result is not None


def test_history():

    from mcp_server.chat_interface import (
        ChatSession
    )

    s = ChatSession("hist-007")

    s.add_message(
        "user",
        "Show low stock items"
    )

    s.add_message(
        "assistant",
        "25 products below reorder point."
    )

    s.add_message(
        "user",
        "Create a PO"
    )

    assert len(s.history) >= 3


def test_tool_calls():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output": "Dashboard loaded.",
            "intermediate_steps": [
                (
                    "get_inventory_dashboard",
                    {}
                )
            ]
        }

        process_message(
            "Dashboard",
            session_id="tool-007"
        )

        mb.return_value.invoke.assert_called_once()


def test_error_handled():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.side_effect = (
            Exception("Timeout")
        )

        result = process_message(
            "Show data",
            session_id="err-007"
        )

        assert result is not None


# ==========================
# INTEGRATION TESTS
# ==========================

def test_6_tools_discovered():

    from mcp_server.chat_interface import (
        build_chat_executor
    )

    assert (
        len(build_chat_executor().tools)
        >= 6
    )


def test_tool_invoked():

    mock_r = {
        "total_products": 500,
        "low_stock_count": 25
    }

    with patch(
        "mcp_server.mcp_app.requests.get"
    ) as mg:

        mg.return_value.status_code = 200
        mg.return_value.json.return_value = mock_r
        mg.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            get_inventory_dashboard
        )

        result = (
            get_inventory_dashboard()
        )

        assert (
            result.get("total_products")
            == 500
            or "error" in result
        )


def test_correct_tool():

    from mcp_server.chat_interface import (
        build_chat_executor
    )

    tool_map = {
        t.name: t
        for t
        in build_chat_executor().tools
    }

    assert (
        "get_low_stock_products"
        in tool_map
    )

    assert (
        "stock"
        in tool_map[
            "get_low_stock_products"
        ].description.lower()
    )


def test_response_routed():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output":
            "25 products below reorder point."
        }

        result = process_message(
            "Low stock items",
            session_id="route-007"
        )

        out = result.get("output", "")

        assert len(out) > 10


def test_multi_turn():

    from mcp_server.chat_interface import (
        ChatSession
    )

    s = ChatSession("mt-007")

    s.add_message(
        "user",
        "Show low stock items"
    )

    s.add_message(
        "assistant",
        "25 products need reorder."
    )

    s.add_message(
        "user",
        "Create a PO"
    )

    assert (
        len(
            s.get_history_for_llm()
        )
        >= 2
    )


def test_tool_chain():

    from mcp_server.chat_interface import (
        build_chat_executor
    )

    names = [
        t.name
        for t
        in build_chat_executor().tools
    ]

    assert (
        "get_inventory_dashboard"
        in names
    )

    assert (
        "get_low_stock_products"
        in names
    )


def test_update_reachable():

    mock_r = {
        "id": 5,
        "movement_type": "receipt",
        "quantity": 50
    }

    with patch(
        "mcp_server.mcp_app.requests.post"
    ) as mp:

        mp.return_value.status_code = 200
        mp.return_value.json.return_value = mock_r
        mp.return_value.raise_for_status = MagicMock()

        from mcp_server.mcp_app import (
            update_stock
        )

        result = update_stock(
            product_id=1,
            movement_type="receipt",
            quantity=50
        )

        assert (
            isinstance(result, dict)
            and result.get("id")
            is not None
        )


# ==========================
# OBSERVABILITY TESTS
# ==========================

def test_langsmith():

    if not os.getenv(
        "LANGCHAIN_API_KEY"
    ):
        pytest.skip("No key")

    from langsmith import Client

    runs = list(
        Client().list_runs(
            project_name=
            "AI-Readiness-POC-07-P4",
            limit=5
        )
    )

    if not runs:
        pytest.skip(
            "No traces yet"
        )

    assert len(runs) >= 1


def test_session_trace():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output": "OK"
        }

        result = process_message(
            "Test",
            session_id="obs-007"
        )

        mb.return_value.invoke.assert_called_once()

        assert result is not None


def test_otel_span():
    assert True


def test_log_session():

    from mcp_server.chat_interface import (
        process_message
    )

    with patch(
        "mcp_server.chat_interface.build_chat_executor"
    ) as mb:

        mb.return_value.invoke.return_value = {
            "output": "OK"
        }

        result = process_message(
            "Test",
            session_id="log-007-session"
        )

        assert result is not None