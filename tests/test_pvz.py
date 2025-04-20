import pytest

@pytest.mark.asyncio
async def test_create_pvz(client, auth_headers_moderator):
    response = await client.post(
        "/api/pvz",
        json={"city": "Москва"},
        headers=auth_headers_moderator
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["city"] == "Москва"

@pytest.mark.asyncio
async def test_list_pvz(client, auth_headers_employee):
    response = await client.get(
        "/api/pvz",
        headers=auth_headers_employee
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
