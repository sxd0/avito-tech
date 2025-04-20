import pytest

@pytest.mark.asyncio
async def test_add_product(client, auth_headers_moderator, auth_headers_employee):
    pvz_resp = await client.post("/api/pvz", json={"city": "Казань"}, headers=auth_headers_moderator)
    pvz_id = pvz_resp.json()["id"]

    await client.post("/api/receptions", json={"pvz_id": pvz_id}, headers=auth_headers_employee)

    response = await client.post("/api/products", json={"type": "электроника", "pvz_id": pvz_id}, headers=auth_headers_employee)
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "электроника"

@pytest.mark.asyncio
async def test_delete_last_product(client, auth_headers_moderator, auth_headers_employee):
    pvz_resp = await client.post("/api/pvz", json={"city": "Казань"}, headers=auth_headers_moderator)
    pvz_id = pvz_resp.json()["id"]

    await client.post("/api/receptions", json={"pvz_id": pvz_id}, headers=auth_headers_employee)
    await client.post("/api/products", json={"type": "одежда", "pvz_id": pvz_id}, headers=auth_headers_employee)

    response = await client.post(f"/api/pvz/{pvz_id}/delete_last_product", headers=auth_headers_employee)
    assert response.status_code == 200
    assert "product_id" in response.json()
