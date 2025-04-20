import pytest
import uuid


@pytest.mark.asyncio
async def test_full_workflow(client, moderator_token, employee_token):
    """
    Интеграционный тест для проверки полного рабочего процесса:
    1. Создание ПВЗ
    2. Добавление новой приемки
    3. Добавление 50 товаров
    4. Закрытие приемки
    """
    pvz_response = client.post(
        "/api/pvz",
        json={"city": "Москва"},
        headers={"Authorization": f"Bearer {moderator_token}"}
    )
    assert pvz_response.status_code == 201
    pvz_id = pvz_response.json()["id"]
    
    reception_response = client.post(
        "/api/receptions",
        json={"pvz_id": pvz_id},
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert reception_response.status_code == 201
    
    product_types = ["электроника", "одежда", "обувь"]
    for i in range(50):
        product_type = product_types[i % 3]
        product_response = client.post(
            "/api/products",
            json={"type": product_type, "pvz_id": pvz_id},
            headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert product_response.status_code == 201
    
    close_response = client.post(
        f"/api/pvz/{pvz_id}/close_last_reception",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert close_response.status_code == 200
    assert close_response.json()["status"] == "close"
    
    product_response = client.post(
        "/api/products",
        json={"type": "электроника", "pvz_id": pvz_id},
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert product_response.status_code == 400