from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.features.auth.schemas import RegisterRequest, RegisterResponse
from app.features.auth.service import register_user
from app.infrastructure.database.config import get_db

from fastapi import HTTPException, status

from app.features.auth.schemas import (
    LoginRequest,
    LoginResponse,
)
from app.features.auth.service import authenticate_user


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
        
    

#login
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

        return LoginResponse(
            access_token="temporary-token",
            token_type="bearer",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )