import pytest

@pytest.mark.asyncio
async def test_add_product(client):
    pvz_resp = await client.post("/pvz", json={"city": "Казань"}, headers={"Authorization": "Bearer test-moderator-token"})
    pvz_id = pvz_resp.json()["id"]

    reception_resp = await client.post("/receptions", json={"pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
    assert reception_resp.status_code == 201

    response = await client.post("/products", json={"type": "электроника", "pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "электроника"

@pytest.mark.asyncio
async def test_delete_last_product(client):
    pvz_resp = await client.post("/pvz", json={"city": "Казань"}, headers={"Authorization": "Bearer test-moderator-token"})
    pvz_id = pvz_resp.json()["id"]

    await client.post("/receptions", json={"pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
    await client.post("/products", json={"type": "одежда", "pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})

    response = await client.post(f"/pvz/{pvz_id}/delete_last_product", headers={"Authorization": "Bearer test-employee-token"})
    assert response.status_code == 200
    assert "product_id" in response.json()
