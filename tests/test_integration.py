import pytest

@pytest.mark.asyncio
async def test_full_flow(client, auth_headers_moderator, auth_headers_employee):
    pvz_resp = await client.post("/api/pvz", json={"city": "Москва"}, headers=auth_headers_moderator)
    assert pvz_resp.status_code == 201
    pvz_id = pvz_resp.json()["id"]

    reception_resp = await client.post("/api/receptions", json={"pvz_id": pvz_id}, headers=auth_headers_employee)
    assert reception_resp.status_code == 201

    for i in range(50):
        product_resp = await client.post("/api/products", json={"type": "обувь", "pvz_id": pvz_id}, headers=auth_headers_employee)
        assert product_resp.status_code == 201

    close_resp = await client.post(f"/api/pvz/{pvz_id}/close_last_reception", headers=auth_headers_employee)
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "closed"
