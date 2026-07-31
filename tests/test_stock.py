def test_low_alerts(client):
    response = client.get(
        "/api/v1/stock/low-alerts"
    )

    assert response.status_code == 200