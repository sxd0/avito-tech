import uuid
import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    email = f"t{uuid.uuid4()}@ex.com"
    r = await client.post("/api/register", json={
        "email": email, "password": "pw", "role": "employee"
    })
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_login_user(client):
    email = f"t{uuid.uuid4()}@ex.com"
    pw = "pw"

    await client.post("/api/register", json={
        "email": email, "password": pw, "role": "employee"
    })

    r = await client.post("/api/login", json={"email": email, "password": pw})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_dummy_login(client):
    ok = await client.post("/api/dummyLogin", json={"role": "moderator"})
    bad = await client.post("/api/dummyLogin", json={"role": "foo"})
    assert ok.status_code == 200
    assert bad.status_code == 400
