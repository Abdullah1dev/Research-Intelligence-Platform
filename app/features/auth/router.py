from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    CurrentUserResponse,
)

from app.features.auth.service import (
    register_user,
    authenticate_user,
)

from app.infrastructure.database.config import get_db

from app.shared.security.jwt import create_access_token

from app.features.users.models import User

from app.shared.enums.roles import UserRole

from app.shared.security.authorization import (
    require_roles,
    get_current_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        return register_user(data, db)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(db, data)

        access_token = create_access_token(
            {
                "sub": str(user.id),
            }
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/admin-test")
def admin_test(
    current_user: User = Depends(
        require_roles(UserRole.ADMIN),
    ),
):
    return {
        "message": "You are an admin",
        "user": current_user.name,
    }