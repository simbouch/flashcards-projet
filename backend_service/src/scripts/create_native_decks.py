"""
Script to create native decks that will always be available in the application.
This script runs automatically when the backend service starts.
It deletes any existing decks and creates three rich native decks.
"""

import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db_module.database import get_db
from db_module.models import User, Deck, Flashcard
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
    """Delete only system-owned decks in the database"""
    logger.info("Deleting existing system-owned decks...")

    # Get only system-owned decks
    existing_decks = db.query(Deck).filter(Deck.owner_id == system_user_id).all()

    for deck in existing_decks:
        logger.info(f"Deleting system deck: {deck.title} (ID: {deck.id})")

        # Delete all flashcards in the deck
        db.query(Flashcard).filter(Flashcard.deck_id == deck.id).delete()

        # Delete the deck
        db.delete(deck)

    # Commit the changes
    db.commit()
    logger.info(f"Deleted {len(existing_decks)} existing system decks")

def create_native_decks(delete_existing=True):
    """Create native decks that will always be available

    Args:
        delete_existing (bool): Whether to delete existing decks before creating new ones
    """
    logger.info("Creating native decks...")

    # Get database session
    db = next(get_db())

    # Create system user
    system_user = create_system_user(db)

    # Delete existing decks if requested
    if delete_existing:
        delete_existing_decks(db, system_user.id)

    # Create each native deck
    for deck_title, flashcards in NATIVE_DECKS.items():
        # Create new deck
        logger.info(f"Creating native deck: {deck_title}")
        new_deck = Deck(
            id=str(uuid.uuid4()),
            title=deck_title,
            description=f"A native deck about {deck_title}",
            is_public=True,
            owner_id=system_user.id
        )

        try:
            db.add(new_deck)
            db.commit()
            db.refresh(new_deck)
            logger.info(f"Created deck: {new_deck.id}")

            # Add flashcards to the deck
            for card_data in flashcards:
                new_card = Flashcard(
                    id=str(uuid.uuid4()),
                    question=card_data["question"],
                    answer=card_data["answer"],
                    deck_id=new_deck.id
                )
                db.add(new_card)

            db.commit()
            logger.info(f"Added {len(flashcards)} flashcards to deck: {deck_title}")

        except IntegrityError as e:
            logger.error(f"Error creating deck {deck_title}: {e}")
            db.rollback()

    logger.info("Native decks creation complete")

if __name__ == "__main__":
    create_native_decks()
