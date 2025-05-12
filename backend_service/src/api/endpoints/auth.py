"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from datetime import timedelta
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import create_access_token, create_refresh_token_for_user
from ...config import settings
from ...logger_config import logger

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
async def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Try to authenticate with username/password
    user = crud.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )

    # Create refresh token
    refresh_token = create_refresh_token_for_user(db, user.id)

    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token.token
    }

@router.post("/refresh", response_model=schemas.Token)
async def refresh_token(
    refresh_data: dict,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using a refresh token.
    """
    refresh_token = refresh_data.get("refresh_token")
    # Validate refresh token
    user = crud.validate_refresh_token(db, refresh_token)
    if not user:
        logger.warning(f"Invalid refresh token used")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )

    # Rotate refresh token (revoke old one and create new one)
    new_refresh_token = crud.rotate_refresh_token(db, refresh_token)
    if not new_refresh_token:
        logger.error(f"Failed to rotate refresh token for user: {user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

    logger.info(f"Refreshed tokens for user: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token.token
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: dict,
    db: Session = Depends(get_db)
) -> None:
    """
    Logout by revoking the refresh token.
    """
    refresh_token = refresh_data.get("refresh_token")
    # Revoke the refresh token
    success = crud.revoke_refresh_token(db, refresh_token)
    if not success:
        logger.warning(f"Failed to revoke refresh token during logout")
        # We don't raise an exception here to allow clients to logout even with invalid tokens

    logger.info("User logged out")
    return None

@router.post("/register", response_model=schemas.User)
async def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    # Check if user with this email already exists
    user = crud.get_user_by_email(db, email=user_in.email)
    if user:
        logger.warning(f"Registration failed: email already exists: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if user with this username already exists
    user = crud.get_user_by_username(db, username=user_in.username)
    if user:
        logger.warning(f"Registration failed: username already exists: {user_in.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    try:
        user = crud.create_user(db, user_in)
        logger.info(f"User registered: {user.username}")
        return user
    except ValueError as e:
        logger.error(f"User registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
