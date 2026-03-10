from typing import Any, Annotated

from fastapi import APIRouter, Form, status

from ..database import SessionDep
from .schemas import AuthForm, UserResponse
from .service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register",
             response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def register(auth: Annotated[AuthForm, Form()], session: SessionDep) -> Any:
    user = await register_user(auth.email, auth.password, session)
    return UserResponse(
        email=user.email,
        username=user.username
    )


@router.post("/verify")
async def verify(token: str, session: SessionDep) -> Any:

    pass


@router.post("/login")
async def login(auth: AuthForm, session: SessionDep) -> Any:
    return