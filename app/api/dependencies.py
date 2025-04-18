from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.dao.users import UsersDAO

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Получение текущего пользователя по токену.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невозможно проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        if user_id.startswith("dummy-"):
            role = payload.get("role")
            return {"id": user_id, "role": role}
    except JWTError:
        raise credentials_exception
    
    user = await UsersDAO.find_one_or_none(id=user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_employee(current_user = Depends(get_current_user)):
    """
    Проверка, что текущий пользователь - сотрудник ПВЗ.
    """
    if current_user.get("role") == "employee" or getattr(current_user, "role", None) == "employee":
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав (требуется роль 'employee')"
    )

async def get_current_moderator(current_user = Depends(get_current_user)):
    """
    Проверка, что текущий пользователь - модератор.
    """
    if current_user.get("role") == "moderator" or getattr(current_user, "role", None) == "moderator":
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав (требуется роль 'moderator')"
    )