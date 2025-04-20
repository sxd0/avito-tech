from typing import Literal
from pydantic import UUID4, BaseModel, EmailStr, ConfigDict


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class DummyLoginSchema(BaseModel):
    role: str
    
    model_config = ConfigDict(from_attributes=True)


class UserSchema(BaseModel):
    id: UUID4
    email: EmailStr
    role: Literal["employee", "moderator"]
    
    model_config = ConfigDict(from_attributes=True)