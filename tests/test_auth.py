def test_register(client):
    response = client.post(
        "/api/v1/auth/register"
    )

    assert response.status_code == 200


def test_login(client):
    response = client.post(
        "/api/v1/auth/login"
    )

    assert response.status_code == 200