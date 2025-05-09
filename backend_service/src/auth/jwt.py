"""
JWT authentication utilities.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from ..config import settings
from ..logger_config import logger
from db_module import crud, models, schemas
from db_module.database import get_db
from sqlalchemy.orm import Session

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token.
        expires_delta: Token expiration time.
        
    Returns:
        JWT token string.
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    
    logger.debug(f"Created access token for user: {data.get('sub')}")
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get the current user from the JWT token.
    
    Args:
        token: JWT token.
        db: Database session.
        
    Returns:
        User object.
        
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Extract user ID from token
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing 'sub' field")
            raise credentials_exception
        
    except JWTError as e:
        logger.warning(f"JWT error: {e}")
        raise credentials_exception
    
    # Get user from database
    user = crud.get_user(db, user_id)
    if user is None:
        logger.warning(f"User not found: {user_id}")
        raise credentials_exception
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    logger.debug(f"Authenticated user: {user.username}")
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user.
        
    Returns:
        User object.
        
    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def is_admin(user: models.User) -> bool:
    """
    Check if user is an admin.
    
    Args:
        user: User to check.
        
    Returns:
        True if user is admin, False otherwise.
    """
    return user.role == models.UserRole.ADMIN.value
