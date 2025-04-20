import pytest

@pytest.mark.asyncio
async def test_create_reception(client, auth_headers_moderator, auth_headers_employee):
    pvz_resp = await client.post("/api/pvz", json={"city": "Санкт-Петербург"}, headers=auth_headers_moderator)
    pvz_id = pvz_resp.json()["id"]

    response = await client.post("/api/receptions", json={"pvz_id": pvz_id}, headers=auth_headers_employee)
    assert response.status_code == 201
    assert response.json()["pvz_id"] == pvz_id

@pytest.mark.asyncio
async def test_close_last_reception(client, auth_headers_moderator, auth_headers_employee):
    pvz_resp = await client.post("/api/pvz", json={"city": "Казань"}, headers=auth_headers_moderator)
    pvz_id = pvz_resp.json()["id"]

    await client.post("/api/receptions", json={"pvz_id": pvz_id}, headers=auth_headers_employee)

    response = await client.post(f"/api/pvz/{pvz_id}/close_last_reception", headers=auth_headers_employee)
    assert response.status_code == 200
    assert response.json()["status"] == "closed"
