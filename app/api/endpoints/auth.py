from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token, create_dummy_token, get_password_hash, verify_password
from app.dao.users import UsersDAO
from app.schemas.auth import DummyLoginSchema, TokenSchema, UserLoginSchema, UserRegisterSchema, UserSchema
from app.logger import logger



router = APIRouter(
    tags=["Аутентификация"]
)

@router.post("/dummyLogin", response_model=TokenSchema)
async def dummy_login(login_data: DummyLoginSchema):
    """
    Тестовый эндпоинт для получения токена с определенной ролью.
    - **role**: Роль пользователя (employee или moderator)
    """
    if login_data.role not in ["employee", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль должна быть 'employee' или 'moderator'"
        )
    
    access_token = create_dummy_token(login_data.role)
    return TokenSchema(access_token=access_token)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterSchema):
    """
    Регистрация нового пользователя.
    - **email**: Email пользователя
    - **password**: Пароль пользователя
    - **role**: Роль пользователя (employee или moderator)
    """
    if user_data.role not in ["employee", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль должна быть 'employee' или 'moderator'"
        )
    
    existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    hashed_password = get_password_hash(user_data.password)
    
    user_data_dict = {
        "email": user_data.email,
        "hashed_password": hashed_password,
        "role": user_data.role,
    }

    user_id = await UsersDAO.add(**user_data_dict)
    # user = await UsersDAO.find_one_or_none(id=user_id)
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if not user:
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")
    logger.info(f"Зарегистрирован новый пользователь: {user_data.email}, роль: {user_data.role}")


    return user

@router.post("/login", response_model=TokenSchema)
async def login_user(user_data: UserLoginSchema):
    """
    Вход пользователя в систему.
    - **username**: Email пользователя
    - **password**: Пароль пользователя
    """
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учётные данные")
    logger.info(f"Пользователь вошел: {user.email}, роль: {user.role}")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}