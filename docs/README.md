# Flashcards Project Database Documentation

This folder contains the complete documentation of the database structure used in the Flashcards project.

## Contents

1. [Conceptual Data Model (CDM)](database_mcd.md) - Conceptual representation of entities and their relationships
2. [Physical Data Model (PDM)](database_mpd.md) - Physical representation of tables and their constraints
3. [Database Schema](database_schema.md) - Overview and class diagram of the database

## Viewing the Diagrams

The diagrams are created using Mermaid syntax. To view them:

1. Open the markdown files in an editor that supports Mermaid (like GitHub, VS Code with the Mermaid extension, etc.)
2. Or copy the content of the Mermaid code blocks into an online editor like [Mermaid Live Editor](https://mermaid.live/)

## Database Structure

The database is organized around several main entities:

### Users and Authentication
- **users**: Stores user information
- **refresh_tokens**: Manages refresh tokens for authentication

### Documents and Processing
- **documents**: Stores metadata for uploaded documents
- **extracted_texts**: Contains text extracted from documents via OCR

### Flashcards and Decks
- **decks**: Represents flashcard decks
- **flashcards**: Stores question/answer cards
- **user_deck_association**: Manages deck sharing between users

### Study and Review
- **study_sessions**: Records study sessions
- **study_records**: Tracks performance for each flashcard

## Technologies Used

- **SQLAlchemy**: ORM (Object-Relational Mapping) for interacting with the database
- **PostgreSQL**: Relational database management system
- **Alembic**: Database migration tool

## Implementation

The implementation code for this schema can be found in:
- `db_module/models.py`: SQLAlchemy model definitions
- `db_module/database.py`: Database connection configuration
- `db_module/schemas.py`: Pydantic schemas for data validation

## Design Considerations

1. **UUID vs Auto-increment**: Using UUIDs for primary keys instead of auto-incremented identifiers for better security and flexibility.

2. **Many-to-Many Relationships**: Using association tables (user_deck_association) to manage many-to-many relationships.

3. **Soft Delete**: No soft delete implementation yet, but could be added by adding a deleted_at field to relevant tables.

4. **Timestamps**: Using created_at and updated_at fields for tracking changes.

5. **Enumerations**: Using enumerations for document statuses and user roles to ensure data consistency.
