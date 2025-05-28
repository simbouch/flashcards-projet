# MLflow Demo Guide

This guide demonstrates how to use MLflow tracking with the OCR and LLM services in the flashcards application.

## Overview

MLflow is integrated into both services to track:
- **OCR Service**: Comprehensive tracking of text extraction operations, confidence scores, and performance metrics
- **LLM Service**: Basic tracking of flashcard generation operations and model performance

## MLflow Setup

### OCR Service MLflow (Comprehensive)
The OCR service uses MLflow extensively to track:
- Text extraction operations
- Confidence scores and filtering statistics
- File processing metrics
- Error tracking and debugging information

### LLM Service MLflow (Minimalistic)
The LLM service uses MLflow for basic tracking:
- Generation requests
- Model performance metrics
- Simple error logging

## Accessing MLflow UI

### OCR MLflow Server
- URL: http://localhost:5000
- Experiment: `ocr_service_tracking`

### LLM MLflow Server  
- URL: http://localhost:5001
- Experiment: `llm_service_tracking`

## Demo Commands

### 1. Start the Services
```bash
docker-compose up -d
```

### 2. Test OCR Service with MLflow Tracking
```bash
# Upload an image for OCR processing
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ocr_service/demo_images/high_quality.png" \
  -F "min_confidence=70"
```

### 3. Test LLM Service with MLflow Tracking
```bash
# Generate flashcards
curl -X POST "http://localhost:8001/generate" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Python is a programming language used for web development and data science.",
    "num_cards": 3
  }'
```

### 4. View MLflow Experiments
Open your browser and navigate to:
- OCR MLflow: http://localhost:5000
- LLM MLflow: http://localhost:5001

## What Gets Tracked

### OCR Service Tracking
- **Run Parameters**: 
  - File name and type
  - Confidence threshold
  - Preprocessing settings
- **Metrics**:
  - Average confidence score
  - Word count (total and filtered)
  - Processing time
  - File size
- **Artifacts**:
  - Confidence distribution charts
  - Processing logs

### LLM Service Tracking
- **Run Parameters**:
  - Input text length
  - Number of cards requested
- **Metrics**:
  - Generation time
  - Number of cards generated
  - Model performance
- **Artifacts**:
  - Generated flashcards (sample)

## Monitoring and Analysis

### OCR Performance Analysis
1. Navigate to OCR MLflow UI
2. Compare runs with different confidence thresholds
3. Analyze confidence score distributions
4. Monitor processing times for different file types

### LLM Performance Analysis
1. Navigate to LLM MLflow UI
2. Track generation success rates
3. Monitor response times
4. Compare different input text lengths

## Troubleshooting

### MLflow Server Not Accessible
1. Check if containers are running: `docker-compose ps`
2. Check logs: `docker-compose logs mlflow-ocr` or `docker-compose logs mlflow-llm`
3. Restart services: `docker-compose restart mlflow-ocr mlflow-llm`

### No Experiments Showing
1. Make sure you've made at least one API call to the services
2. Refresh the MLflow UI
3. Check service logs for MLflow connection errors

## Best Practices

### For OCR Service
- Use confidence thresholds to filter low-quality text
- Monitor confidence distributions to optimize preprocessing
- Track file types and sizes for performance optimization

### For LLM Service
- Monitor generation times to optimize model performance
- Track success rates for different input types
- Use feedback data for model improvement

## Integration with Monitoring

MLflow data can be integrated with:
- Prometheus metrics for alerting
- Grafana dashboards for visualization
- Custom analytics pipelines for model improvement

## Next Steps

1. Set up automated model retraining based on MLflow data
2. Implement A/B testing for different model configurations
3. Create custom MLflow plugins for specialized tracking
4. Integrate with CI/CD pipelines for model deployment
