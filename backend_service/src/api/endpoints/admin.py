"""Admin-only endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_admin_user
from ...logger_config import logger


router = APIRouter()


def _is_system_user(user: models.User) -> bool:
    return bool(user) and (user.username or "").lower() == "system"


@router.get("/stats")
async def admin_stats(
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Basic system statistics for admin dashboard."""
    return {
        "users_total": db.query(models.User).count(),
        "admins_total": crud.count_admin_users(db),
        "documents_total": db.query(models.Document).count(),
        "decks_total": db.query(models.Deck).count(),
        "flashcards_total": db.query(models.Flashcard).count(),
    }


@router.get("/users", response_model=List[schemas.User])
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Any:
    return crud.get_users(db, skip=skip, limit=limit)


@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    user_in: schemas.AdminUserCreate,
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Any:
    """Create a user as an admin (role + is_active supported)."""
    if (user_in.username or "").lower() == "system":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username 'system' is reserved",
        )
    try:
        created = crud.admin_create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    logger.info(f"Admin created user {created.username}")
    return created


@router.patch("/users/{user_id}", response_model=schemas.User)
async def admin_update_user(
    user_id: str,
    user_in: schemas.UserAdminUpdate,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Any:
    target = crud.get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if _is_system_user(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System user cannot be modified",
        )

    update_data = user_in.model_dump(exclude_unset=True)

    if (update_data.get("username") or "").lower() == "system":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username 'system' is reserved",
        )

    # Prevent admin from locking themselves out
    if user_id == current_admin.id:
        if "role" in update_data and update_data["role"] != models.UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin cannot change their own role",
            )
        if update_data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin cannot deactivate themselves",
            )

    # Prevent removing the last admin
    is_target_admin = target.role == models.UserRole.ADMIN.value
    if is_target_admin and crud.count_admin_users(db) <= 1:
        if update_data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last admin",
            )
        if "role" in update_data and update_data["role"] != models.UserRole.ADMIN.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last admin",
            )

    try:
        updated = crud.admin_update_user(db, user_id, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"Admin updated user {updated.username}")
    return updated


@router.post("/users/{user_id}/reset-password", response_model=schemas.User)
async def admin_reset_password(
    user_id: str,
    payload: schemas.AdminResetPassword,
    _: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Any:
    target = crud.get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if _is_system_user(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System user password cannot be reset",
        )

    user = crud.set_user_password(db, user_id, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: str,
    current_admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> None:
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot delete themselves",
        )

    target = crud.get_user(db, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if _is_system_user(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System user cannot be deleted",
        )

    if target.role == models.UserRole.ADMIN.value and crud.count_admin_users(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last admin",
        )

    ok = crud.delete_user(db, user_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
