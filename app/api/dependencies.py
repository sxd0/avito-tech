from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.dao.users import UsersDAO
from app.database import async_session_maker


token_auth_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
):
    """
    Извлекаем текущего пользователя из JWTтокена.
    """
    token = credentials.credentials
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Невозможно проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exc

        if user_id.startswith("dummy-"):
            return {"id": user_id, "role": payload.get("role")}

    except JWTError:
        raise credentials_exc

    async with async_session_maker() as session:
        user = await UsersDAO(session).find_one_or_none(id=user_id)
        if user is None:
            raise credentials_exc
        return user


async def get_current_employee(current_user=Depends(get_current_user)):
    """
    Доступ разрешён сотруднику ПВЗ (role == "employee").
    """
    role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if role == "employee":
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав (требуется роль 'employee')",
    )


async def get_current_moderator(current_user=Depends(get_current_user)):
    """
    Доступ разрешён модератору (role == "moderator").
    """
    role = current_user.get("role") if isinstance(current_user, dict) else current_user.role
    if role == "moderator":
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Недостаточно прав (требуется роль 'moderator')",
    )
