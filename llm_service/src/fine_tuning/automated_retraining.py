#!/usr/bin/env python3
"""
Automated retraining system for flashcard generation model.
Includes performance monitoring, data drift detection, and scheduled retraining.
"""

import os
import json
import time
import schedule
import mlflow
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
from loguru import logger

from training_pipeline import FlashcardTrainer, FineTuningConfig
from ..model_evaluator import ModelEvaluator
from ..data_collector import DataCollector

@dataclass
class RetrainingConfig:
    """Configuration for automated retraining system."""
    # Scheduling
    retraining_schedule: str = "weekly"  # daily, weekly, monthly
    retraining_time: str = "02:00"  # Time to run retraining (24h format)
    
    # Performance thresholds
    min_accuracy_threshold: float = 0.75
    max_response_time_threshold: float = 30.0  # seconds
    min_user_satisfaction_threshold: float = 0.8
    
    # Data requirements
    min_new_samples_for_retraining: int = 100
    data_drift_threshold: float = 0.3
    
    # Model management
    max_models_to_keep: int = 5
    model_registry_name: str = "flashcard_generator"
    
    # Monitoring
    metrics_collection_interval: int = 3600  # seconds (1 hour)
    performance_window_days: int = 7

class PerformanceMonitor:
    """Monitor model performance and collect metrics."""
    
    def __init__(self, config: RetrainingConfig):
        self.config = config
        self.metrics_history = []
        
    def collect_performance_metrics(self) -> Dict[str, float]:
        """Collect current model performance metrics."""
        try:
            # Get recent model predictions and user feedback
            evaluator = ModelEvaluator()
            
            # Calculate performance metrics
            metrics = {
                'accuracy': evaluator.calculate_accuracy(),
                'response_time': evaluator.calculate_avg_response_time(),
                'user_satisfaction': evaluator.calculate_user_satisfaction(),
                'generation_success_rate': evaluator.calculate_success_rate(),
                'timestamp': time.time()
            }
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Log to MLflow
            with mlflow.start_run():
                mlflow.log_metrics({
                    f"performance_{k}": v for k, v in metrics.items() 
                    if k != 'timestamp'
                })
            
            logger.info(f"Performance metrics collected: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
            return {}
    
    def check_performance_degradation(self) -> bool:
        """Check if model performance has degraded below thresholds."""
        if len(self.metrics_history) < 2:
            return False
            
        recent_metrics = self.metrics_history[-1]
        
        # Check individual thresholds
        degradation_flags = [
            recent_metrics.get('accuracy', 1.0) < self.config.min_accuracy_threshold,
            recent_metrics.get('response_time', 0.0) > self.config.max_response_time_threshold,
            recent_metrics.get('user_satisfaction', 1.0) < self.config.min_user_satisfaction_threshold
        ]
        
        if any(degradation_flags):
            logger.warning(f"Performance degradation detected: {recent_metrics}")
            return True
            
        return False

class DataDriftDetector:
    """Detect data drift in incoming requests."""
    
    def __init__(self, config: RetrainingConfig):
        self.config = config
        self.baseline_distribution = None
        
    def set_baseline_distribution(self, baseline_data: List[Dict[str, Any]]):
        """Set baseline data distribution for drift detection."""
        # Extract features from baseline data
        features = self._extract_features(baseline_data)
        self.baseline_distribution = self._calculate_distribution(features)
        
    def detect_drift(self, new_data: List[Dict[str, Any]]) -> bool:
        """Detect if new data has drifted from baseline."""
        if self.baseline_distribution is None:
            logger.warning("No baseline distribution set for drift detection")
            return False
            
        # Extract features from new data
        new_features = self._extract_features(new_data)
        new_distribution = self._calculate_distribution(new_features)
        
        # Calculate drift score (simplified KL divergence)
        drift_score = self._calculate_drift_score(
            self.baseline_distribution, 
            new_distribution
        )
        
        is_drift = drift_score > self.config.data_drift_threshold
        
        if is_drift:
            logger.warning(f"Data drift detected! Drift score: {drift_score}")
            
        return is_drift
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> Dict[str, List]:
        """Extract relevant features from data for drift detection."""
        features = {
            'text_length': [],
            'subject_distribution': [],
            'difficulty_distribution': [],
            'language_distribution': []
        }
        
        for item in data:
            text = item.get('text', '')
            features['text_length'].append(len(text))
            features['subject_distribution'].append(item.get('subject', 'unknown'))
            features['difficulty_distribution'].append(item.get('difficulty', 'medium'))
            # Simple language detection (could be improved)
            features['language_distribution'].append(self._detect_language(text))
            
        return features
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection (placeholder)."""
        # This is a simplified version - use proper language detection in production
        french_words = ['le', 'la', 'les', 'de', 'du', 'des', 'et', 'ou', 'est']
        english_words = ['the', 'and', 'or', 'is', 'are', 'of', 'to', 'in', 'for']
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return 'french' if french_count > english_count else 'english'
    
    def _calculate_distribution(self, features: Dict[str, List]) -> Dict[str, Any]:
        """Calculate statistical distribution of features."""
        distribution = {}
        
        # Numerical features
        if features['text_length']:
            distribution['text_length_mean'] = np.mean(features['text_length'])
            distribution['text_length_std'] = np.std(features['text_length'])
        
        # Categorical features
        for cat_feature in ['subject_distribution', 'difficulty_distribution', 'language_distribution']:
            if features[cat_feature]:
                unique, counts = np.unique(features[cat_feature], return_counts=True)
                distribution[cat_feature] = dict(zip(unique, counts / len(features[cat_feature])))
        
        return distribution
    
    def _calculate_drift_score(self, baseline: Dict, current: Dict) -> float:
        """Calculate drift score between distributions."""
        # Simplified drift calculation
        drift_score = 0.0
        
        # Compare numerical features
        for feature in ['text_length_mean', 'text_length_std']:
            if feature in baseline and feature in current:
                diff = abs(baseline[feature] - current[feature])
                drift_score += diff / (baseline[feature] + 1e-8)
        
        # Compare categorical distributions
        for cat_feature in ['subject_distribution', 'difficulty_distribution', 'language_distribution']:
            if cat_feature in baseline and cat_feature in current:
                baseline_dist = baseline[cat_feature]
                current_dist = current[cat_feature]
                
                # Calculate KL divergence (simplified)
                for category in set(list(baseline_dist.keys()) + list(current_dist.keys())):
                    p = baseline_dist.get(category, 1e-8)
                    q = current_dist.get(category, 1e-8)
                    drift_score += p * np.log(p / q)
        
        return drift_score

class AutomatedRetrainingSystem:
    """Main automated retraining system."""
    
    def __init__(self, config: RetrainingConfig):
        self.config = config
        self.performance_monitor = PerformanceMonitor(config)
        self.drift_detector = DataDriftDetector(config)
        self.data_collector = DataCollector()
        self.is_running = False
        
    def start_monitoring(self):
        """Start the automated monitoring and retraining system."""
        logger.info("Starting automated retraining system...")
        
        # Schedule performance monitoring
        schedule.every(self.config.metrics_collection_interval).seconds.do(
            self.performance_monitor.collect_performance_metrics
        )
        
        # Schedule retraining based on configuration
        if self.config.retraining_schedule == "daily":
            schedule.every().day.at(self.config.retraining_time).do(self.check_and_retrain)
        elif self.config.retraining_schedule == "weekly":
            schedule.every().week.at(self.config.retraining_time).do(self.check_and_retrain)
        elif self.config.retraining_schedule == "monthly":
            schedule.every(30).days.at(self.config.retraining_time).do(self.check_and_retrain)
        
        self.is_running = True
        
        # Main monitoring loop
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.is_running = False
        logger.info("Automated retraining system stopped")
    
    def check_and_retrain(self):
        """Check if retraining is needed and execute if necessary."""
        logger.info("Checking if retraining is needed...")
        
        try:
            # Check performance degradation
            performance_degraded = self.performance_monitor.check_performance_degradation()
            
            # Check data availability
            new_data = self.data_collector.get_new_training_data()
            sufficient_data = len(new_data) >= self.config.min_new_samples_for_retraining
            
            # Check data drift
            data_drift = self.drift_detector.detect_drift(new_data) if new_data else False
            
            # Determine if retraining is needed
            should_retrain = performance_degraded or (sufficient_data and data_drift)
            
            if should_retrain:
                logger.info("Retraining triggered!")
                self.execute_retraining(new_data)
            else:
                logger.info("No retraining needed at this time")
                
        except Exception as e:
            logger.error(f"Error during retraining check: {e}")
    
    def execute_retraining(self, training_data: List[Dict[str, Any]]):
        """Execute the retraining process."""
        logger.info("Starting automated retraining...")
        
        try:
            # Create training configuration
            config = FineTuningConfig()
            trainer = FlashcardTrainer(config)
            
            # Execute training with MLflow tracking
            experiment_name = f"automated_retraining_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = trainer.train(training_data, experiment_name)
            
            # Evaluate new model
            evaluator = ModelEvaluator()
            evaluation_results = evaluator.evaluate_model(model_path)
            
            # Deploy if evaluation passes
            if evaluation_results['accuracy'] > self.config.min_accuracy_threshold:
                self.deploy_new_model(model_path)
                logger.info("New model deployed successfully!")
            else:
                logger.warning("New model failed evaluation, keeping current model")
                
            # Clean up old models
            self.cleanup_old_models()
            
        except Exception as e:
            logger.error(f"Error during retraining: {e}")
    
    def deploy_new_model(self, model_path: str):
        """Deploy the newly trained model."""
        # This would integrate with your model serving infrastructure
        # For now, we'll just log the deployment
        logger.info(f"Deploying model from: {model_path}")
        
        # Register model in MLflow
        mlflow.register_model(
            f"file://{model_path}",
            self.config.model_registry_name
        )
    
    def cleanup_old_models(self):
        """Clean up old model versions to save storage."""
        try:
            client = mlflow.tracking.MlflowClient()
            model_versions = client.get_latest_versions(
                self.config.model_registry_name,
                stages=["Production", "Staging", "Archived"]
            )
            
            if len(model_versions) > self.config.max_models_to_keep:
                # Archive oldest models
                versions_to_archive = sorted(
                    model_versions, 
                    key=lambda x: x.creation_timestamp
                )[:-self.config.max_models_to_keep]
                
                for version in versions_to_archive:
                    client.transition_model_version_stage(
                        self.config.model_registry_name,
                        version.version,
                        "Archived"
                    )
                    
                logger.info(f"Archived {len(versions_to_archive)} old model versions")
                
        except Exception as e:
            logger.error(f"Error cleaning up old models: {e}")

if __name__ == "__main__":
    # Example usage
    config = RetrainingConfig()
    retraining_system = AutomatedRetrainingSystem(config)
    
    try:
        retraining_system.start_monitoring()
    except KeyboardInterrupt:
        retraining_system.stop_monitoring()
        logger.info("Automated retraining system stopped by user")
