#!/usr/bin/env python3
"""
Data collection system for continuous learning and model improvement.
Collects user interactions, feedback, and new educational content.
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("Pandas not available, some features disabled")

@dataclass
class UserInteraction:
    """User interaction data structure."""
    session_id: str
    user_id: Optional[str]
    input_text: str
    generated_cards: List[Dict[str, str]]
    response_time: float
    timestamp: datetime
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    user_feedback: Optional[Dict[str, Any]] = None

@dataclass
class UserFeedback:
    """User feedback data structure."""
    interaction_id: str
    rating: int  # 1-5 scale
    feedback_text: Optional[str]
    card_quality_rating: Optional[int]
    educational_value_rating: Optional[int]
    timestamp: datetime

class DataCollector:
    """Collect and manage training data from user interactions."""

    def __init__(self, db_path: str = "data/training_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for data storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # User interactions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        user_id TEXT,
                        input_text TEXT NOT NULL,
                        generated_cards TEXT NOT NULL,
                        response_time REAL NOT NULL,
                        subject TEXT,
                        difficulty TEXT,
                        timestamp DATETIME NOT NULL,
                        processed BOOLEAN DEFAULT FALSE
                    )
                """)

                # User feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        interaction_id INTEGER NOT NULL,
                        rating INTEGER NOT NULL,
                        feedback_text TEXT,
                        card_quality_rating INTEGER,
                        educational_value_rating INTEGER,
                        timestamp DATETIME NOT NULL,
                        FOREIGN KEY (interaction_id) REFERENCES user_interactions (id)
                    )
                """)

                # Educational content table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS educational_content (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        source TEXT,
                        quality_score REAL,
                        timestamp DATETIME NOT NULL,
                        processed BOOLEAN DEFAULT FALSE
                    )
                """)

                # Model performance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS model_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_version TEXT NOT NULL,
                        accuracy REAL,
                        response_time REAL,
                        user_satisfaction REAL,
                        success_rate REAL,
                        timestamp DATETIME NOT NULL
                    )
                """)

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error setting up database: {e}")

    def record_user_interaction(self, interaction: UserInteraction) -> int:
        """Record a user interaction in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO user_interactions
                    (session_id, user_id, input_text, generated_cards, response_time,
                     subject, difficulty, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.session_id,
                    interaction.user_id,
                    interaction.input_text,
                    json.dumps(interaction.generated_cards),
                    interaction.response_time,
                    interaction.subject,
                    interaction.difficulty,
                    interaction.timestamp
                ))

                interaction_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Recorded user interaction: {interaction_id}")
                return interaction_id

        except Exception as e:
            logger.error(f"Error recording user interaction: {e}")
            return -1

    def record_user_feedback(self, feedback: UserFeedback):
        """Record user feedback in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO user_feedback
                    (interaction_id, rating, feedback_text, card_quality_rating,
                     educational_value_rating, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    feedback.interaction_id,
                    feedback.rating,
                    feedback.feedback_text,
                    feedback.card_quality_rating,
                    feedback.educational_value_rating,
                    feedback.timestamp
                ))

                conn.commit()
                logger.info(f"Recorded user feedback for interaction: {feedback.interaction_id}")

        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")

    def add_educational_content(self, title: str, content: str, subject: str,
                              difficulty: str, source: str = None, quality_score: float = None):
        """Add new educational content for training."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO educational_content
                    (title, content, subject, difficulty, source, quality_score, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    title,
                    content,
                    subject,
                    difficulty,
                    source,
                    quality_score,
                    datetime.now()
                ))

                conn.commit()
                logger.info(f"Added educational content: {title}")

        except Exception as e:
            logger.error(f"Error adding educational content: {e}")

    def get_new_training_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get new training data from user interactions and educational content."""
        training_data = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get unprocessed user interactions with positive feedback
                cursor.execute("""
                    SELECT ui.input_text, ui.generated_cards, ui.subject, ui.difficulty,
                           AVG(uf.rating) as avg_rating
                    FROM user_interactions ui
                    LEFT JOIN user_feedback uf ON ui.id = uf.interaction_id
                    WHERE ui.processed = FALSE
                    GROUP BY ui.id
                    HAVING avg_rating >= 4 OR avg_rating IS NULL
                    LIMIT ?
                """, (limit // 2,))

                interaction_data = cursor.fetchall()

                for row in interaction_data:
                    input_text, generated_cards, subject, difficulty, avg_rating = row

                    training_data.append({
                        'text': input_text,
                        'subject': subject or 'General',
                        'difficulty': difficulty or 'Medium',
                        'generated_cards': json.loads(generated_cards),
                        'quality_score': avg_rating or 3.0,
                        'source': 'user_interaction'
                    })

                # Get unprocessed educational content
                cursor.execute("""
                    SELECT title, content, subject, difficulty, quality_score
                    FROM educational_content
                    WHERE processed = FALSE
                    LIMIT ?
                """, (limit // 2,))

                content_data = cursor.fetchall()

                for row in content_data:
                    title, content, subject, difficulty, quality_score = row

                    training_data.append({
                        'text': content,
                        'subject': subject,
                        'difficulty': difficulty,
                        'title': title,
                        'quality_score': quality_score or 3.0,
                        'source': 'educational_content'
                    })

                # Mark data as processed
                if interaction_data:
                    cursor.execute("""
                        UPDATE user_interactions
                        SET processed = TRUE
                        WHERE processed = FALSE AND id IN (
                            SELECT ui.id FROM user_interactions ui
                            LEFT JOIN user_feedback uf ON ui.id = uf.interaction_id
                            GROUP BY ui.id
                            HAVING AVG(uf.rating) >= 4 OR AVG(uf.rating) IS NULL
                            LIMIT ?
                        )
                    """, (limit // 2,))

                if content_data:
                    cursor.execute("""
                        UPDATE educational_content
                        SET processed = TRUE
                        WHERE processed = FALSE
                        LIMIT ?
                    """, (limit // 2,))

                conn.commit()

                logger.info(f"Retrieved {len(training_data)} new training samples")

        except Exception as e:
            logger.error(f"Error getting new training data: {e}")

        return training_data

    def get_performance_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get model performance data for the specified period."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cutoff_date = datetime.now() - timedelta(days=days)

                cursor.execute("""
                    SELECT model_version, accuracy, response_time, user_satisfaction,
                           success_rate, timestamp
                    FROM model_performance
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                """, (cutoff_date,))

                performance_data = []
                for row in cursor.fetchall():
                    performance_data.append({
                        'model_version': row[0],
                        'accuracy': row[1],
                        'response_time': row[2],
                        'user_satisfaction': row[3],
                        'success_rate': row[4],
                        'timestamp': row[5]
                    })

                logger.info(f"Retrieved {len(performance_data)} performance records")
                return performance_data

        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return []

    def record_model_performance(self, model_version: str, accuracy: float,
                                response_time: float, user_satisfaction: float,
                                success_rate: float):
        """Record model performance metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO model_performance
                    (model_version, accuracy, response_time, user_satisfaction,
                     success_rate, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    model_version,
                    accuracy,
                    response_time,
                    user_satisfaction,
                    success_rate,
                    datetime.now()
                ))

                conn.commit()
                logger.info(f"Recorded performance for model: {model_version}")

        except Exception as e:
            logger.error(f"Error recording model performance: {e}")

    def get_user_feedback_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get summary of user feedback for the specified period."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cutoff_date = datetime.now() - timedelta(days=days)

                cursor.execute("""
                    SELECT AVG(rating) as avg_rating,
                           COUNT(*) as total_feedback,
                           AVG(card_quality_rating) as avg_quality,
                           AVG(educational_value_rating) as avg_educational_value
                    FROM user_feedback
                    WHERE timestamp >= ?
                """, (cutoff_date,))

                result = cursor.fetchone()

                summary = {
                    'average_rating': result[0] or 0.0,
                    'total_feedback': result[1] or 0,
                    'average_quality_rating': result[2] or 0.0,
                    'average_educational_value': result[3] or 0.0,
                    'period_days': days
                }

                logger.info(f"User feedback summary: {summary}")
                return summary

        except Exception as e:
            logger.error(f"Error getting user feedback summary: {e}")
            return {}

    def export_training_data(self, output_path: str, format: str = 'json'):
        """Export training data for external processing."""
        try:
            training_data = self.get_new_training_data(limit=10000)

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(training_data, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                if PANDAS_AVAILABLE:
                    df = pd.DataFrame(training_data)
                    df.to_csv(output_file, index=False)
                else:
                    # Simple CSV export without pandas
                    import csv
                    if training_data:
                        with open(output_file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=training_data[0].keys())
                            writer.writeheader()
                            writer.writerows(training_data)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported {len(training_data)} training samples to {output_file}")

        except Exception as e:
            logger.error(f"Error exporting training data: {e}")

    def cleanup_old_data(self, days: int = 90):
        """Clean up old data to manage storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cutoff_date = datetime.now() - timedelta(days=days)

                # Clean up old processed interactions
                cursor.execute("""
                    DELETE FROM user_interactions
                    WHERE processed = TRUE AND timestamp < ?
                """, (cutoff_date,))

                deleted_interactions = cursor.rowcount

                # Clean up old performance data
                cursor.execute("""
                    DELETE FROM model_performance
                    WHERE timestamp < ?
                """, (cutoff_date,))

                deleted_performance = cursor.rowcount

                conn.commit()

                logger.info(f"Cleaned up {deleted_interactions} interactions and {deleted_performance} performance records")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

# Example usage and testing
if __name__ == "__main__":
    collector = DataCollector()

    # Example interaction
    interaction = UserInteraction(
        session_id="test_session_123",
        user_id="user_456",
        input_text="Machine learning is a subset of artificial intelligence.",
        generated_cards=[
            {"question": "What is machine learning?", "answer": "A subset of artificial intelligence"}
        ],
        response_time=25.5,
        timestamp=datetime.now(),
        subject="Computer Science",
        difficulty="Intermediate"
    )

    interaction_id = collector.record_user_interaction(interaction)

    # Example feedback
    feedback = UserFeedback(
        interaction_id=str(interaction_id),
        rating=4,
        feedback_text="Good quality flashcard",
        card_quality_rating=4,
        educational_value_rating=5,
        timestamp=datetime.now()
    )

    collector.record_user_feedback(feedback)

    # Get training data
    training_data = collector.get_new_training_data(limit=10)
    print(f"Retrieved {len(training_data)} training samples")
