"""
User management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List
from sqlalchemy.orm import Session

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_active_user, is_admin
from ...logger_config import logger

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user.
    """
    user = crud.update_user(db, current_user.id, user_in)
    logger.info(f"User updated: {user.username}")
    return user


@router.post("/me/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_account(
    payload: schemas.UserDeleteSelf,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete the currently authenticated user's account.

    Requires password confirmation.
    """
    # Defensive: reserved internal account must never be deletable.
    if (current_user.username or "").strip().lower() == "system":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System account cannot be deleted",
        )

    if not crud.verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    # Prevent deleting the last admin account
    if is_admin(current_user) and crud.count_admin_users(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last admin account",
        )

    ok = crud.delete_user(db, current_user.id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account",
        )

    logger.info(f"User self-deleted: {current_user.username}")
    return None

@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve users.
    """
    # Check if user is admin
    if not is_admin(current_user):
        logger.warning(f"Non-admin user {current_user.username} attempted to list all users")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.User)
async def read_user(
    user_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get user by ID.
    """
    # Users can only access their own data unless they are admins
    if user_id != current_user.id and not is_admin(current_user):
        logger.warning(f"User {current_user.username} attempted to access user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: str,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update user.
    """
    # Only admins can update other users
    if user_id != current_user.id and not is_admin(current_user):
        logger.warning(f"User {current_user.username} attempted to update user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = crud.get_user(db, user_id)
    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = crud.update_user(db, user_id, user_in)
    logger.info(f"User updated: {user.username}")
    return user
