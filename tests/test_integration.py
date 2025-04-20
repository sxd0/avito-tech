import pytest

@pytest.mark.asyncio
async def test_full_flow(client):
    pvz_resp = await client.post("/pvz", json={"city": "Москва"}, headers={"Authorization": "Bearer test-moderator-token"})
    assert pvz_resp.status_code == 201
    pvz_id = pvz_resp.json()["id"]

    reception_resp = await client.post("/receptions", json={"pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
    assert reception_resp.status_code == 201

    for i in range(50):
        product_resp = await client.post("/products", json={"type": "обувь", "pvz_id": pvz_id}, headers={"Authorization": "Bearer test-employee-token"})
        assert product_resp.status_code == 201

    close_resp = await client.post(f"/pvz/{pvz_id}/close_last_reception", headers={"Authorization": "Bearer test-employee-token"})
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"