import pytest


@pytest.mark.asyncio
async def test_create_pvz(client, moderator_token):
    response = client.post(
        "/api/pvz",
        json={"city": "Москва"},
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert response.status_code == 201
    assert response.json()["city"] == "Москва"
    
    response = client.post(
        "/api/pvz",
        json={"city": "Новосибирск"},
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_pvz_list(client, moderator_token):
    client.post(
        "/api/pvz",
        json={"city": "Санкт-Петербург"},
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    
    response = client.get(
        "/api/pvz",
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)