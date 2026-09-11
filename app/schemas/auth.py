from pydantic import BaseModel, EmailStr


class UserRegistration(BaseModel):
    email: EmailStr
    password: str


class UserRegistrationResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
