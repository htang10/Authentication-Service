from pydantic import BaseModel, EmailStr, Field


class AuthForm(BaseModel):
    email: EmailStr = Field(min_length=16, max_length=254)
    password: str = Field(min_length=8, max_length=64)

class UserResponse(BaseModel):
    email: str
    username: str

