import pytest

@pytest.mark.asyncio
async def test_create_pvz(client):
    response = await client.post(
        "/pvz",
        json={"city": "Москва"},
        headers={"Authorization": "Bearer test-moderator-token"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["city"] == "Москва"

@pytest.mark.asyncio
async def test_list_pvz(client):
    response = await client.get(
        "/pvz",
        headers={"Authorization": "Bearer test-user-token"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)