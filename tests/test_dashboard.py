def test_dashboard(client):
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