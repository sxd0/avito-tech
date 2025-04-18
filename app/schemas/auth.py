from pydantic import BaseModel, EmailStr, ConfigDict


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
    id: str
    email: EmailStr
    role: str
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)