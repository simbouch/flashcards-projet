"""
API routes for the backend service.
"""
from fastapi import APIRouter
from .endpoints import auth, users, documents, decks, flashcards, study

# Create API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(study.router, prefix="/study", tags=["study"])
