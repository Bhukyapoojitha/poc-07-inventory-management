import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_create_product(client):
    payload = {
        "name": "Basmati Rice 5kg",
        "category": "grocery",
        "unit_price": 350.0,
        "cost_price": 280.0,
        "reorder_point": 20,
        "reorder_quantity": 100
    }

    response = client.post(
        "/api/v1/products",
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert data["sku"].startswith("SKU-GRO-")


def test_stock_update_alert(client):
    product_payload = {
        "name": "Test Rice",
        "category": "grocery",
        "unit_price": 350.0,
        "cost_price": 280.0,
        "reorder_point": 20,
        "reorder_quantity": 100
    }

    product_response = client.post(
        "/api/v1/products",
        json=product_payload
    )

    assert product_response.status_code == 201

    product = product_response.json()

    response = client.patch(
        f"/api/v1/products/{product['id']}/stock",
        json={
            "movement_type": "sale",
            "quantity": -1000,
            "reference_number": "SALE-001",
            "notes": "Bulk sale"
        }
    )

    assert response.status_code == 200

    alerts = client.get(
        "/api/v1/stock/low-alerts"
    )

    assert alerts.status_code == 200


def test_create_po(client):
    products_response = client.get(
        "/api/v1/products"
    )

    assert products_response.status_code == 200

    products = products_response.json()

    if len(products) == 0:
        return

    product_id = products[0]["id"]

    payload = {
        "supplier_id": 1,
        "order_date": "2026-07-31",
        "expected_delivery": "2026-08-05",
        "items": [
            {
                "product_id": product_id,
                "quantity_ordered": 100,
                "unit_cost": 280.0
            }
        ]
    }

    response = client.post(
        "/api/v1/orders",
        json=payload
    )

    assert response.status_code == 201

    data = response.json()

    assert "po_number" in data
    assert data["po_number"].startswith("PO-")
    assert data["status"] == "draft"


def test_receive_po(client):
    response = client.get(
        "/api/v1/orders"
    )

    assert response.status_code == 200

    orders = response.json()

    if len(orders) == 0:
        return

    po_id = orders[0]["id"]

    receive_response = client.patch(
        f"/api/v1/orders/{po_id}/receive"
    )

    assert receive_response.status_code == 200


def test_low_alerts(client):
    response = client.get(
        "/api/v1/stock/low-alerts"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_supplier_catalog(client):
    response = client.get(
        "/api/v1/suppliers/1/catalog"
    )

    assert response.status_code == 200

    assert isinstance(response.json(), list)


def test_filter_category(client):
    response = client.get(
        "/api/v1/products?category=grocery"
    )

    assert response.status_code == 200

    for product in response.json():
        assert product["category"] == "grocery"


def test_dashboard_fields(client):
    response = client.get(
        "/api/v1/dashboard"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_products" in data
    assert "low_stock_count" in data
    assert "out_of_stock_count" in data
    assert "open_po_count" in data
    assert "total_stock_value" in data