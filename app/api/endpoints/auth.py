from fastapi import APIRouter, HTTPException, status
from app.core.security import (
    create_access_token,
    create_dummy_token,
    get_password_hash,
    verify_password,
)
from app.dao.users import UsersDAO
from app.database import async_session_maker
from app.schemas.auth import (
    DummyLoginSchema,
    TokenSchema,
    UserLoginSchema,
    UserRegisterSchema,
    UserSchema,
)
from app.logger import logger

router = APIRouter(tags=["Аутентификация"])


# ---------- Dummy ----------------------------------------------------
@router.post("/dummyLogin", response_model=TokenSchema)
async def dummy_login(data: DummyLoginSchema):
    if data.role not in ("employee", "moderator"):
        raise HTTPException(400, "role must be 'employee' or 'moderator'")
    return TokenSchema(access_token=create_dummy_token(data.role))


# ---------- Register -------------------------------------------------
@router.post("/register", response_model=UserSchema, status_code=201)
async def register_user(data: UserRegisterSchema):
    if data.role not in ("employee", "moderator"):
        raise HTTPException(400, "role must be 'employee' or 'moderator'")

    async with async_session_maker() as session:
        dao = UsersDAO(session)

        if await dao.find_one_or_none(email=data.email):
            raise HTTPException(400, "email already exists")

        await dao.add(
            {
                "email": data.email,
                "hashed_password": get_password_hash(data.password),
                "role": data.role,
            }
        )
        await session.commit()

        user = await dao.find_one_or_none(email=data.email)
        logger.info("User registered: %s [%s]", data.email, data.role)
        return user


# ---------- Login ----------------------------------------------------
@router.post("/login", response_model=TokenSchema)
async def login_user(data: UserLoginSchema):
    async with async_session_maker() as session:
        dao = UsersDAO(session)
        user = await dao.find_one_or_none(email=data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")

        logger.info("User login: %s [%s]", user.email, user.role)
        token = create_access_token({"sub": str(user.id), "role": user.role})
        return {"access_token": token, "token_type": "bearer"}
