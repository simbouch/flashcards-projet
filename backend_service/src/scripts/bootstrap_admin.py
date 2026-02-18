"""Admin bootstrap helpers.

Creates an initial admin user on startup if configured via env vars.
"""

import os

from db_module import crud, models, schemas
from db_module.database import SessionLocal

from ..config import settings
from ..logger_config import logger


def bootstrap_initial_admin() -> None:
    """Create initial admin user if configured.

    Rules:
    - No-op when TESTING=true
    - Requires INITIAL_ADMIN_USERNAME + INITIAL_ADMIN_PASSWORD
    - If an admin already exists -> no-op
    - If username/email already exists:
        - promote to admin only when INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING=true
        - otherwise skip with warning
    """

    if os.getenv("TESTING", "false").lower() == "true":
        return

    username = (settings.INITIAL_ADMIN_USERNAME or "").strip()
    password = settings.INITIAL_ADMIN_PASSWORD or ""
    if not username or not password:
        return

    email = (settings.INITIAL_ADMIN_EMAIL or "").strip() or f"{username}@example.com"
    full_name = (settings.INITIAL_ADMIN_FULL_NAME or "").strip() or "Initial Admin"

    db = SessionLocal()
    try:
        # If any admin exists already, do nothing
        if crud.count_admin_users(db) > 0:
            return

        existing_by_username = crud.get_user_by_username(db, username)
        existing_by_email = crud.get_user_by_email(db, email)
        existing = existing_by_username or existing_by_email

        if existing:
            if not settings.INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING:
                logger.warning(
                    "Initial admin bootstrap skipped: user exists but promotion disabled "
                    "(set INITIAL_ADMIN_ALLOW_PROMOTE_EXISTING=true to allow)."
                )
                return
            existing.role = models.UserRole.ADMIN.value
            existing.is_active = True
            db.commit()
            logger.info(f"Promoted existing user to admin: {existing.username}")
            return

        # Create brand-new admin user (validates password strength via schema)
        user_in = schemas.UserCreate(
            email=email,
            username=username,
            password=password,
            full_name=full_name,
        )
        crud.create_user_with_role(db, user_in, role=models.UserRole.ADMIN.value)
        logger.info(f"Initial admin created: {username}")
    except Exception as e:
        logger.error(f"Initial admin bootstrap failed: {type(e).__name__}: {e}")
    finally:
        db.close()
