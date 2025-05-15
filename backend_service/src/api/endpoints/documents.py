"""
Document management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from typing import Any, List
from sqlalchemy.orm import Session
import uuid
import os
import aiofiles
from pathlib import Path

from db_module import crud, models, schemas
from db_module.database import get_db
from ...auth.jwt import get_current_active_user
from ...config import settings
from ...logger_config import logger
from ...services.ocr_service import OCRServiceClient
from ...services.llm_service import LLMServiceClient

router = APIRouter()

# Initialize service clients
ocr_client = OCRServiceClient()
llm_client = LLMServiceClient()

async def process_document(
    document_id: str,
    file_path: Path,
    db: Session
):
    """
    Process a document: extract text with OCR and generate flashcards.

    Args:
        document_id: ID of the document to process.
        file_path: Path to the document file.
        db: Database session.
    """
    try:
        # Update document status to OCR processing
        crud.update_document_status(
            db, document_id, models.DocumentStatus.OCR_PROCESSING.value
        )

        # Extract text with OCR
        ocr_result = await ocr_client.extract_text(file_path)
        extracted_text = ocr_result.get("text", "")

        # Save extracted text to database
        text_data = schemas.ExtractedTextCreate(
            content=extracted_text,
            document_id=document_id
        )
        crud.create_extracted_text(db, text_data)

        # Update document status to OCR complete
        crud.update_document_status(
            db, document_id, models.DocumentStatus.OCR_COMPLETE.value
        )

        # Update document status to flashcard generating
        crud.update_document_status(
            db, document_id, models.DocumentStatus.FLASHCARD_GENERATING.value
        )

        # Generate flashcards
        flashcard_result = await llm_client.generate_flashcards(extracted_text, num_cards=10)

        # Create a deck for the flashcards
        document = crud.get_document(db, document_id)
        deck_name = f"Deck for {document.filename}"

        deck_data = schemas.DeckCreate(
            title=deck_name,
            description=f"Automatically generated from {document.filename}",
            document_id=document_id
        )
        deck = crud.create_deck(db, deck_data, owner_id=document.owner_id)

        # Save flashcards to database
        for card in flashcard_result.get("flashcards", []):
            flashcard_data = schemas.FlashcardCreate(
                question=card["question"],
                answer=card["answer"],
                deck_id=deck.id
            )
            crud.create_flashcard(db, flashcard_data)

        # Update document status to complete
        crud.update_document_status(
            db, document_id, models.DocumentStatus.FLASHCARD_COMPLETE.value
        )

        logger.info(f"Document processing complete: {document_id}")

    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {str(e)}")
        # Update document status to error
        crud.update_document_status(
            db, document_id, models.DocumentStatus.ERROR.value, str(e)
        )

@router.post("/", response_model=schemas.Document)
async def create_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload a new document.
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower().lstrip(".")
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        logger.warning(f"Invalid file extension: {file_ext}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = settings.UPLOAD_DIR / unique_filename

    # Save file
    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            await f.write(content)
    except Exception as e:
        logger.exception(f"Error saving file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    # Create document in database
    document_data = schemas.DocumentCreate(
        filename=file.filename,
        mime_type=file.content_type or f"image/{file_ext}"
    )
    document = crud.create_document(
        db, document_data, current_user.id, str(file_path)
    )

    # Process document in background
    background_tasks.add_task(
        process_document, document.id, file_path, db
    )

    logger.info(f"Document created: {document.id}")
    return document

@router.get("/", response_model=List[schemas.Document])
async def read_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Retrieve documents.
    """
    documents = crud.get_documents_by_owner(
        db, current_user.id, skip=skip, limit=limit
    )
    return documents

@router.get("/{document_id}", response_model=schemas.Document)
async def read_document(
    document_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get document by ID.
    """
    document = crud.get_document(db, document_id)
    if not document:
        logger.warning(f"Document not found: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if user is the owner
    if document.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to access document {document_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    return document

@router.get("/{document_id}/text", response_model=schemas.ExtractedText)
async def read_document_text(
    document_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get extracted text for a document.
    """
    document = crud.get_document(db, document_id)
    if not document:
        logger.warning(f"Document not found: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if user is the owner
    if document.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to access document text {document_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Get extracted text
    extracted_text = crud.get_extracted_text_by_document(db, document_id)
    if not extracted_text:
        logger.warning(f"Extracted text not found for document: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Extracted text not found"
        )

    return extracted_text

@router.delete("/{document_id}", response_model=schemas.Document)
async def delete_document(
    document_id: str,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a document.
    """
    document = crud.get_document(db, document_id)
    if not document:
        logger.warning(f"Document not found: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    # Check if user is the owner
    if document.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} attempted to delete document {document_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Delete file
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        logger.error(f"Error deleting file {document.file_path}: {str(e)}")

    # Delete extracted text first (if exists)
    extracted_text = crud.get_extracted_text_by_document(db, document_id)
    if extracted_text:
        logger.info(f"Deleting extracted text for document: {document_id}")
        crud.delete_extracted_text(db, extracted_text.id)

    # Delete document from database
    crud.delete_document(db, document_id)

    logger.info(f"Document deleted: {document_id}")
    return document
