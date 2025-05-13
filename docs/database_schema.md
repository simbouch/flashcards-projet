# Database Schema

## Overview

The database schema for the Flashcards project is designed to manage:
- Users and authentication
- Uploaded documents and extracted text
- Flashcard decks and individual cards
- Study sessions and performance tracking

## Database Diagram

```mermaid
classDiagram
    class User {
        +String id
        +String email
        +String username
        +String hashed_password
        +String full_name
        +String role
        +Boolean is_active
        +DateTime created_at
        +DateTime updated_at
    }

    class Document {
        +String id
        +String filename
        +String file_path
        +String mime_type
        +String status
        +Text error_message
        +DateTime created_at
        +DateTime updated_at
        +String owner_id
    }

    class ExtractedText {
        +String id
        +Text content
        +DateTime created_at
        +String document_id
    }

    class Deck {
        +String id
        +String title
        +Text description
        +Boolean is_public
        +DateTime created_at
        +DateTime updated_at
        +String owner_id
        +String document_id
    }

    class Flashcard {
        +String id
        +Text question
        +Text answer
        +DateTime created_at
        +DateTime updated_at
        +String deck_id
    }

    class StudySession {
        +String id
        +DateTime started_at
        +DateTime ended_at
        +String user_id
        +String deck_id
    }

    class StudyRecord {
        +String id
        +Float ease_factor
        +Integer interval
        +Boolean is_correct
        +DateTime created_at
        +String session_id
        +String flashcard_id
    }

    class RefreshToken {
        +String id
        +String token
        +DateTime expires_at
        +Boolean revoked
        +DateTime created_at
        +String user_id
    }

    class UserDeckAssociation {
        +String user_id
        +String deck_id
    }

    User "1" --> "*" Document : owns
    User "1" --> "*" Deck : owns
    User "1" --> "*" StudySession : participates
    User "1" --> "*" RefreshToken : has
    User "1" --> "*" UserDeckAssociation : has
    Deck "1" --> "*" UserDeckAssociation : shared with

    Document "1" --> "0..1" ExtractedText : has
    Document "1" --> "*" Deck : generates

    Deck "1" --> "*" Flashcard : contains
    Deck "1" --> "*" StudySession : used in

    StudySession "1" --> "*" StudyRecord : contains
    Flashcard "1" --> "*" StudyRecord : referenced in
```

## Data Flow

1. **Document Upload and Processing**:
   - A user uploads a document
   - The document is processed by the OCR service to extract text
   - The extracted text is used by the LLM service to generate flashcards
   - A deck is created with the generated flashcards

2. **Study and Review**:
   - A user selects a deck to study
   - A study session is created
   - For each flashcard reviewed, a study record is created
   - Performance metrics are used to adjust the spaced repetition algorithm

3. **Deck Sharing**:
   - A user can share their decks with other users
   - Shared decks are accessible via the user_deck_association table

## Key Features

1. **UUID Identification**: All entities use UUIDs as primary keys for better security and flexibility.

2. **Timestamps**: Most tables include created_at and updated_at fields for tracking changes.

3. **Document Statuses**: Documents go through different processing states (uploaded, ocr_processing, ocr_complete, flashcard_generating, flashcard_complete, error).

4. **Spaced Repetition Algorithm**: The ease_factor and interval fields in StudyRecord are used to implement the SM-2 spaced repetition algorithm.

5. **Secure Authentication**: Use of access and refresh tokens for authentication.

6. **Flexible Relationships**: A document can generate multiple decks, and a deck can exist independently of a document (document_id is nullable in Deck).

## Performance Considerations

1. **Indexing**: Frequently searched fields like email, username, and token are indexed.

2. **Uniqueness Constraints**: UNIQUE constraints are applied to email, username, token, and document_id in extracted_texts.

3. **Referential Integrity**: Foreign keys are used to maintain data integrity between tables.
