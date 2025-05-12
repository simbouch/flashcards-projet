"""
Pydantic schemas for API validation and serialization.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
import re
from uuid import UUID

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class TokenPayload(BaseModel):
    sub: str
    exp: datetime

class RefreshTokenCreate(BaseModel):
    user_id: str
    token: str
    expires_at: datetime

class RefreshTokenInDB(BaseModel):
    id: str
    token: str
    user_id: str
    expires_at: datetime
    revoked: bool
    created_at: datetime

    class Config:
        orm_mode = True

class RefreshToken(RefreshTokenInDB):
    pass

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric with optional underscores and hyphens')
        return v

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    id: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class User(UserInDB):
    pass

# Document schemas
class DocumentBase(BaseModel):
    filename: str
    mime_type: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None

class DocumentInDB(DocumentBase):
    id: str
    file_path: str
    status: str
    error_message: Optional[str] = None
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Document(DocumentInDB):
    pass

# ExtractedText schemas
class ExtractedTextBase(BaseModel):
    content: str

class ExtractedTextCreate(ExtractedTextBase):
    document_id: str

class ExtractedTextInDB(ExtractedTextBase):
    id: str
    document_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class ExtractedText(ExtractedTextInDB):
    pass

# Deck schemas
class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False

class DeckCreate(DeckBase):
    document_id: Optional[str] = None

class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class DeckInDB(DeckBase):
    id: str
    owner_id: str
    document_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Deck(DeckInDB):
    pass

class DeckWithFlashcards(Deck):
    flashcards: List['Flashcard'] = []

# Flashcard schemas
class FlashcardBase(BaseModel):
    question: str
    answer: str

class FlashcardCreate(FlashcardBase):
    deck_id: str

class FlashcardUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

class FlashcardInDB(FlashcardBase):
    id: str
    deck_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Flashcard(FlashcardInDB):
    pass

# Study session schemas
class StudySessionBase(BaseModel):
    deck_id: str

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    ended_at: datetime

class StudySessionInDB(StudySessionBase):
    id: str
    user_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class StudySession(StudySessionInDB):
    pass

# Study record schemas
class StudyRecordBase(BaseModel):
    is_correct: bool

class StudyRecordCreate(StudyRecordBase):
    session_id: str
    flashcard_id: str

class StudyRecordInDB(StudyRecordBase):
    id: str
    session_id: str
    flashcard_id: str
    ease_factor: float
    interval: int
    created_at: datetime

    class Config:
        orm_mode = True

class StudyRecord(StudyRecordInDB):
    pass

# Update forward references for nested models
DeckWithFlashcards.update_forward_refs()
