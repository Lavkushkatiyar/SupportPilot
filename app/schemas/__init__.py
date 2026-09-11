from pydantic import BaseModel, EmailStr


class UserRegistration(BaseModel):
    email: EmailStr
    password: str


class UserRegistrationResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}
