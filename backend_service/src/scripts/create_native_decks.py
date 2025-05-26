"""
Script to create native decks that will always be available in the application.
This script runs automatically when the backend service starts.
It deletes any existing decks and creates three rich native decks.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db_module.database import get_db
from db_module.models import User, Deck, Flashcard, StudySession, StudyRecord
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample flashcards for different subjects
NATIVE_DECKS = {
    "Programming Concepts": [
        {
            "question": "What is a variable?",
            "answer": "A named storage location in memory that holds a value."
        },
        {
            "question": "What is object-oriented programming?",
            "answer": "A programming paradigm based on the concept of 'objects', which can contain data and code."
        },
        {
            "question": "What is a function?",
            "answer": "A reusable block of code that performs a specific task."
        },
        {
            "question": "What is inheritance in OOP?",
            "answer": "A mechanism where a class can inherit properties and methods from another class."
        },
        {
            "question": "What is a data structure?",
            "answer": "A specialized format for organizing, processing, retrieving and storing data."
        },
        {
            "question": "What is an algorithm?",
            "answer": "A step-by-step procedure or set of rules for solving a specific problem or accomplishing a task."
        },
        {
            "question": "What is polymorphism in OOP?",
            "answer": "The ability of different objects to respond to the same method call in different ways."
        },
        {
            "question": "What is encapsulation in OOP?",
            "answer": "The bundling of data and methods that operate on that data within a single unit (class)."
        },
        {
            "question": "What is recursion?",
            "answer": "A programming technique where a function calls itself to solve a problem."
        },
        {
            "question": "What is a stack?",
            "answer": "A linear data structure that follows the Last In, First Out (LIFO) principle."
        }
    ],
    "World Capitals": [
        {
            "question": "What is the capital of France?",
            "answer": "Paris"
        },
        {
            "question": "What is the capital of Japan?",
            "answer": "Tokyo"
        },
        {
            "question": "What is the capital of Brazil?",
            "answer": "Brasília"
        },
        {
            "question": "What is the capital of Australia?",
            "answer": "Canberra"
        },
        {
            "question": "What is the capital of Egypt?",
            "answer": "Cairo"
        },
        {
            "question": "What is the capital of Canada?",
            "answer": "Ottawa"
        },
        {
            "question": "What is the capital of Germany?",
            "answer": "Berlin"
        },
        {
            "question": "What is the capital of South Korea?",
            "answer": "Seoul"
        },
        {
            "question": "What is the capital of Mexico?",
            "answer": "Mexico City"
        },
        {
            "question": "What is the capital of India?",
            "answer": "New Delhi"
        }
    ],
    "Science Facts": [
        {
            "question": "What is photosynthesis?",
            "answer": "The process by which green plants and some other organisms use sunlight to synthesize foods with carbon dioxide and water."
        },
        {
            "question": "What is the chemical symbol for gold?",
            "answer": "Au (from the Latin 'aurum')"
        },
        {
            "question": "What is Newton's First Law of Motion?",
            "answer": "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force."
        },
        {
            "question": "What is the speed of light in a vacuum?",
            "answer": "299,792,458 meters per second"
        },
        {
            "question": "What is the smallest unit of life?",
            "answer": "The cell"
        },
        {
            "question": "What is DNA?",
            "answer": "Deoxyribonucleic acid, a molecule that carries genetic instructions for the development, functioning, growth and reproduction of all known organisms."
        },
        {
            "question": "What is the periodic table?",
            "answer": "A tabular arrangement of chemical elements, organized by their atomic number, electron configuration, and recurring chemical properties."
        },
        {
            "question": "What is the greenhouse effect?",
            "answer": "The warming of Earth's surface and lower atmosphere caused by gases that trap heat, such as carbon dioxide and methane."
        },
        {
            "question": "What is the theory of relativity?",
            "answer": "A theory developed by Albert Einstein that describes the relationship between space and time, and how gravity affects them."
        },
        {
            "question": "What is the Big Bang theory?",
            "answer": "The prevailing cosmological model explaining the existence of the observable universe from the earliest known periods through its subsequent large-scale evolution."
        }
    ]
}

def create_system_user(db: Session):
    """Create a system user if it doesn't exist"""
    system_user = db.query(User).filter(User.username == "system").first()

    if not system_user:
        logger.info("Creating system user")
        system_user = User(
            id=str(uuid.uuid4()),
            username="system",
            email="system@example.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="System User",
            is_active=True,
            role="system"
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
        logger.info(f"System user created with ID: {system_user.id}")

    return system_user

def delete_existing_decks(db: Session, system_user_id: str):
    """Delete only system-owned decks and all related records in the database"""
    logger.info("Deleting existing system-owned decks and related records...")

    try:
        # Get only system-owned decks
        existing_decks = db.query(Deck).filter(Deck.owner_id == system_user_id).all()

        if not existing_decks:
            logger.info("No existing system decks found to delete")
            return

        deck_ids = [deck.id for deck in existing_decks]
        logger.info(f"Found {len(existing_decks)} system decks to delete: {[deck.title for deck in existing_decks]}")

        # Step 1: Delete study records for sessions related to these decks
        study_sessions_to_delete = db.query(StudySession).filter(StudySession.deck_id.in_(deck_ids)).all()
        session_ids = [session.id for session in study_sessions_to_delete]

        if session_ids:
            logger.info(f"Deleting {len(session_ids)} study sessions and their records")

            # Delete study records first (they reference study sessions)
            study_records_deleted = db.query(StudyRecord).filter(StudyRecord.session_id.in_(session_ids)).delete(synchronize_session=False)
            logger.info(f"Deleted {study_records_deleted} study records")

            # Delete study sessions (they reference decks)
            study_sessions_deleted = db.query(StudySession).filter(StudySession.deck_id.in_(deck_ids)).delete(synchronize_session=False)
            logger.info(f"Deleted {study_sessions_deleted} study sessions")

        # Step 2: Delete flashcards for these decks
        for deck in existing_decks:
            flashcards_deleted = db.query(Flashcard).filter(Flashcard.deck_id == deck.id).delete(synchronize_session=False)
            logger.info(f"Deleted {flashcards_deleted} flashcards from deck: {deck.title}")

        # Step 3: Delete the decks themselves
        for deck in existing_decks:
            logger.info(f"Deleting system deck: {deck.title} (ID: {deck.id})")
            db.delete(deck)

        # Commit all changes
        db.commit()
        logger.info(f"Successfully deleted {len(existing_decks)} system decks and all related records")

    except Exception as e:
        logger.error(f"Error during deck deletion: {str(e)}")
        db.rollback()
        raise

def create_native_decks(delete_existing=True):
    """Create native decks that will always be available

    Args:
        delete_existing (bool): Whether to delete existing decks before creating new ones
    """
    logger.info("Starting native decks creation process...")
    db = None

    try:
        # Get database session
        db = next(get_db())
        logger.info("Database session established")

        # Create system user
        system_user = create_system_user(db)
        logger.info(f"System user ready: {system_user.username}")

        # Delete existing decks if requested
        if delete_existing:
            logger.info("Cleaning up existing system decks...")
            delete_existing_decks(db, system_user.id)
            logger.info("Cleanup completed successfully")

        # Create each native deck
        created_decks = 0
        total_flashcards = 0

        for deck_title, flashcards in NATIVE_DECKS.items():
            try:
                # Create new deck
                logger.info(f"Creating native deck: {deck_title}")
                new_deck = Deck(
                    id=str(uuid.uuid4()),
                    title=deck_title,
                    description=f"A native deck about {deck_title}",
                    is_public=True,
                    owner_id=system_user.id
                )

                db.add(new_deck)
                db.commit()
                db.refresh(new_deck)
                logger.info(f"Created deck: {new_deck.id}")

                # Add flashcards to the deck
                flashcard_count = 0
                for card_data in flashcards:
                    new_card = Flashcard(
                        id=str(uuid.uuid4()),
                        question=card_data["question"],
                        answer=card_data["answer"],
                        deck_id=new_deck.id
                    )
                    db.add(new_card)
                    flashcard_count += 1

                db.commit()
                logger.info(f"Added {flashcard_count} flashcards to deck: {deck_title}")

                created_decks += 1
                total_flashcards += flashcard_count

            except IntegrityError as e:
                logger.error(f"Integrity error creating deck {deck_title}: {e}")
                db.rollback()
                raise
            except Exception as e:
                logger.error(f"Unexpected error creating deck {deck_title}: {e}")
                db.rollback()
                raise

        logger.info(f"Native decks creation completed successfully!")
        logger.info(f"Summary: Created {created_decks} decks with {total_flashcards} total flashcards")

    except Exception as e:
        logger.error(f"Critical error during native decks creation: {str(e)}")
        if db:
            try:
                db.rollback()
                logger.info("Database transaction rolled back")
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        raise
    finally:
        if db:
            try:
                db.close()
                logger.info("Database session closed")
            except Exception as close_error:
                logger.error(f"Error closing database session: {close_error}")

if __name__ == "__main__":
    create_native_decks()
