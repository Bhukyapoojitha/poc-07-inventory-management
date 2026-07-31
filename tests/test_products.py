def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200


def test_get_products(client):
    response = client.get(
        "/api/v1/products"
    )

    assert response.status_code == 200