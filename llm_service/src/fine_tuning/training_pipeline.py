#!/usr/bin/env python3
"""
Fine-tuning pipeline for educational flashcard generation.
Integrates with MLflow for experiment tracking and model versioning.
"""

import os
import json
import torch
import mlflow
import mlflow.pytorch
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from datasets import Dataset
from loguru import logger
import pandas as pd

@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning process."""
    model_name: str = "bigscience/bloom-560m"
    output_dir: str = "./fine_tuned_models"
    num_train_epochs: int = 3
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    warmup_steps: int = 100
    weight_decay: float = 0.01
    learning_rate: float = 5e-5
    logging_steps: int = 10
    save_steps: int = 500
    eval_steps: int = 500
    max_length: int = 512
    gradient_accumulation_steps: int = 4
    fp16: bool = True
    dataloader_num_workers: int = 2

class FlashcardDataProcessor:
    """Process educational data for flashcard fine-tuning."""
    
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        
    def create_training_examples(self, educational_texts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Create training examples from educational content.
        
        Args:
            educational_texts: List of educational content with metadata
            
        Returns:
            List of formatted training examples
        """
        examples = []
        
        for item in educational_texts:
            text = item.get('text', '')
            subject = item.get('subject', 'General')
            difficulty = item.get('difficulty', 'Medium')
            
            # Create multiple flashcards per text
            flashcards = self._extract_concepts(text, subject, difficulty)
            
            for card in flashcards:
                # Format as instruction-following example
                prompt = self._create_prompt(text, subject, difficulty)
                response = self._format_flashcard_response(card)
                
                examples.append({
                    'input': prompt,
                    'output': response,
                    'text': prompt + response
                })
                
        return examples
    
    def _extract_concepts(self, text: str, subject: str, difficulty: str) -> List[Dict[str, str]]:
        """Extract key concepts from text for flashcard creation."""
        # This is a simplified version - in production, use more sophisticated NLP
        sentences = text.split('. ')
        concepts = []
        
        for i, sentence in enumerate(sentences[:3]):  # Limit to 3 concepts per text
            if len(sentence.strip()) > 20:  # Filter short sentences
                concepts.append({
                    'question': f"What is the key concept in: '{sentence[:50]}...'?",
                    'answer': sentence.strip(),
                    'subject': subject,
                    'difficulty': difficulty
                })
                
        return concepts
    
    def _create_prompt(self, text: str, subject: str, difficulty: str) -> str:
        """Create instruction prompt for flashcard generation."""
        return f"""### Instruction:
Create educational flashcards from the following {subject} text at {difficulty} difficulty level.
Generate clear, concise question-answer pairs that test key concepts.

### Text:
{text[:300]}...

### Response:
"""

    def _format_flashcard_response(self, card: Dict[str, str]) -> str:
        """Format flashcard as structured response."""
        return f"""{{
    "question": "{card['question']}",
    "answer": "{card['answer']}",
    "subject": "{card['subject']}",
    "difficulty": "{card['difficulty']}"
}}"""

class FlashcardTrainer:
    """Fine-tuning trainer for flashcard generation."""
    
    def __init__(self, config: FineTuningConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.data_processor = None
        
    def setup_model_and_tokenizer(self):
        """Initialize model and tokenizer."""
        logger.info(f"Loading model: {self.config.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.fp16 else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        self.data_processor = FlashcardDataProcessor(self.tokenizer)
        
    def prepare_dataset(self, training_data: List[Dict[str, Any]]) -> Dataset:
        """Prepare dataset for training."""
        logger.info("Preparing training dataset...")
        
        # Process educational texts into training examples
        examples = self.data_processor.create_training_examples(training_data)
        
        # Tokenize examples
        def tokenize_function(examples):
            return self.tokenizer(
                examples['text'],
                truncation=True,
                padding=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            )
        
        # Create dataset
        dataset = Dataset.from_pandas(pd.DataFrame(examples))
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        return tokenized_dataset
    
    def train(self, training_data: List[Dict[str, Any]], experiment_name: str = "flashcard_finetuning"):
        """Execute fine-tuning process with MLflow tracking."""
        
        # Start MLflow experiment
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run():
            # Log configuration
            mlflow.log_params({
                "model_name": self.config.model_name,
                "num_epochs": self.config.num_train_epochs,
                "batch_size": self.config.per_device_train_batch_size,
                "learning_rate": self.config.learning_rate,
                "max_length": self.config.max_length,
                "training_samples": len(training_data)
            })
            
            # Setup model and data
            self.setup_model_and_tokenizer()
            train_dataset = self.prepare_dataset(training_data)
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                num_train_epochs=self.config.num_train_epochs,
                per_device_train_batch_size=self.config.per_device_train_batch_size,
                per_device_eval_batch_size=self.config.per_device_eval_batch_size,
                warmup_steps=self.config.warmup_steps,
                weight_decay=self.config.weight_decay,
                learning_rate=self.config.learning_rate,
                logging_steps=self.config.logging_steps,
                save_steps=self.config.save_steps,
                eval_steps=self.config.eval_steps,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                fp16=self.config.fp16,
                dataloader_num_workers=self.config.dataloader_num_workers,
                report_to=None,  # Disable wandb/tensorboard
                save_total_limit=3,
                load_best_model_at_end=True,
                metric_for_best_model="loss",
                greater_is_better=False,
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,  # Causal LM, not masked LM
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer,
            )
            
            # Train model
            logger.info("Starting fine-tuning...")
            train_result = trainer.train()
            
            # Log training metrics
            mlflow.log_metrics({
                "train_loss": train_result.training_loss,
                "train_runtime": train_result.metrics["train_runtime"],
                "train_samples_per_second": train_result.metrics["train_samples_per_second"],
            })
            
            # Save model
            model_path = f"{self.config.output_dir}/final_model"
            trainer.save_model(model_path)
            
            # Log model to MLflow
            mlflow.pytorch.log_model(
                pytorch_model=self.model,
                artifact_path="model",
                registered_model_name="flashcard_generator"
            )
            
            # Log tokenizer
            self.tokenizer.save_pretrained(f"{model_path}/tokenizer")
            mlflow.log_artifacts(f"{model_path}/tokenizer", "tokenizer")
            
            logger.info("Fine-tuning completed successfully!")
            
            return model_path

def create_sample_training_data() -> List[Dict[str, Any]]:
    """Create sample educational data for demonstration."""
    return [
        {
            "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions or decisions based on those patterns.",
            "subject": "Computer Science",
            "difficulty": "Intermediate"
        },
        {
            "text": "Photosynthesis is the process by which plants convert light energy into chemical energy. During this process, plants use sunlight, carbon dioxide, and water to produce glucose and oxygen. This process is essential for life on Earth as it provides oxygen for breathing and food for the food chain.",
            "subject": "Biology",
            "difficulty": "Beginner"
        },
        {
            "text": "The French Revolution was a period of radical political and societal change in France from 1789 to 1799. It was characterized by the overthrow of the monarchy, the establishment of a republic, and significant social and economic reforms. The revolution had lasting impacts on French society and influenced democratic movements worldwide.",
            "subject": "History",
            "difficulty": "Advanced"
        }
    ]

if __name__ == "__main__":
    # Example usage
    config = FineTuningConfig()
    trainer = FlashcardTrainer(config)
    
    # Create sample data
    training_data = create_sample_training_data()
    
    # Train model
    model_path = trainer.train(training_data)
    print(f"Model saved to: {model_path}")
