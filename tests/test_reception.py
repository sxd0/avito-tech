import pytest

@pytest.mark.asyncio
async def test_create_reception(client):
    pvz_resp = await client.post("/pvz", json={"city": "Санкт-Петербург"}, headers={"Authorization": "Bearer test-moderator-token"})
    pvz_id = pvz_resp.json()["id"]

    response = await client.post("/receptions", json={"pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
    assert response.status_code == 201
    assert response.json()["pvz_id"] == pvz_id

@pytest.mark.asyncio
async def test_close_last_reception(client):
    pvz_resp = await client.post("/pvz", json={"city": "Казань"}, headers={"Authorization": "Bearer test-moderator-token"})
    pvz_id = pvz_resp.json()["id"]

    await client.post("/receptions", json={"pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})

    response = await client.post(f"/pvz/{pvz_id}/close_last_reception", headers={"Authorization": "Bearer test-employee-token"})
    assert response.status_code == 200
    assert response.json()["status"] == "closed"