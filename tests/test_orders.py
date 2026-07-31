def test_get_orders(client):
    response = client.get(
        "/api/v1/orders"
    )

    assert response.status_code == 200