import pytest
from app.dao.users import UsersDAO
from app.core.security import get_password_hash


@pytest.mark.asyncio
async def test_register_user(client):
    response = client.post("/api/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "role": "employee"
    })
    assert response.status_code == 201
    assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


@pytest.mark.asyncio
async def test_login_user(client):
    await UsersDAO.add(
        email="login_test@example.com",
        hashed_password=get_password_hash("testpassword"),
        role="employee"
    )
    
    response = client.post("/api/login", json={
        "email": "login_test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_dummy_login(client):
    response = client.post("/api/dummyLogin", json={"role": "moderator"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    response = client.post("/api/dummyLogin", json={"role": "invalid_role"})
    assert response.status_code == 400