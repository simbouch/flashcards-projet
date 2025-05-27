# Flashcards Application - Complete Monitoring Guide

## 🎯 Overview

This guide covers the comprehensive monitoring stack implemented for the entire Flashcards application, including all services: Backend, OCR, LLM, Frontend, Database, and Redis.

## 🏗️ Architecture

### Monitoring Stack Components

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards
3. **AlertManager** - Alert handling and notifications
4. **Node Exporter** - System-level metrics
5. **cAdvisor** - Container metrics
6. **Redis Exporter** - Redis-specific metrics
7. **MLflow** - ML model tracking (OCR service)

### Application Services Monitored

1. **Backend Service** (Port 8002)
   - API request metrics
   - Authentication operations
   - Database operations
   - Study session tracking
   - File upload monitoring

2. **OCR Service** (Port 8000)
   - Document processing metrics
   - Confidence score tracking
   - MLflow integration
   - File type analysis

3. **LLM Service** (Port 8001)
   - AI generation metrics
   - Token usage tracking
   - Model performance
   - Memory usage monitoring

4. **Frontend Service** (Port 8080)
   - User interaction metrics
   - Page load times
   - Error tracking

5. **Infrastructure Services**
   - Redis cache performance
   - Database operations
   - Container resource usage
   - System metrics

## 🚀 Quick Start

### 1. Start Complete Monitoring Stack

```bash
# Make script executable
chmod +x start_monitoring.sh

# Start monitoring (includes rebuilding services with metrics)
./start_monitoring.sh
```

### 2. Access Monitoring Interfaces

- **Grafana Dashboard**: http://localhost:3000 (admin/flashcards2024)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093
- **MLflow**: http://localhost:5000

## 📊 Available Dashboards

### 1. Complete Overview Dashboard
**Purpose**: High-level view of entire application health
**Key Metrics**:
- Service health status for all components
- Request rates across all services
- Response times and error rates
- Resource usage (CPU, Memory)
- Active users and operations

### 2. Backend Service Dashboard
**Purpose**: Detailed backend API monitoring
**Key Metrics**:
- Request rate by endpoint
- Response time distribution
- Authentication operations
- Database operation tracking
- Study session metrics
- File upload statistics

### 3. OCR Service Dashboard
**Purpose**: Document processing and ML monitoring
**Key Metrics**:
- OCR operation rates by file type
- Processing time analysis
- Confidence score distributions
- Word extraction statistics
- MLflow tracking integration
- Error analysis by type

### 4. LLM Service Dashboard
**Purpose**: AI generation and performance monitoring
**Key Metrics**:
- Generation request rates
- Processing time distributions
- Token usage statistics
- Model memory usage
- Success/failure rates
- Error categorization

## 🔍 Key Metrics Explained

### Backend Service Metrics

```prometheus
# Request tracking
backend_requests_total{method, endpoint, status}
backend_request_duration_seconds{method, endpoint}

# Business logic
backend_active_users
backend_study_sessions_total{status}
backend_deck_operations_total{operation, status}
backend_auth_operations_total{operation, status}

# Infrastructure
backend_database_operations_total{operation, table, status}
backend_external_api_calls_total{service, status}
```

### OCR Service Metrics

```prometheus
# Core operations
ocr_operations_total{status, file_type}
ocr_processing_duration_seconds{file_type}
ocr_active_requests

# Quality metrics
ocr_confidence_score{file_type}
ocr_word_count{file_type}
ocr_filtered_words{file_type}

# File analysis
ocr_file_size_bytes{file_type}
```

### LLM Service Metrics

```prometheus
# Generation tracking
llm_generation_requests_total{request_type, status}
llm_generation_duration_seconds{request_type}
llm_flashcards_generated_total{request_type}

# Performance
llm_active_generations
llm_model_memory_usage_bytes
llm_token_usage{token_type}

# Reliability
llm_generation_errors_total{error_type}
```

## 🚨 Alerting Rules

### Critical Alerts
- **Service Down**: Any service unavailable for >1 minute
- **High Error Rate**: >10% error rate for >2 minutes
- **Database Connection Failures**: >3 failures in 5 minutes
- **Container Restart Loop**: >3 restarts in 10 minutes

### Warning Alerts
- **High Response Time**: 95th percentile >10s for OCR, >30s for LLM
- **Low OCR Confidence**: Average <50% for 10 minutes
- **High Memory Usage**: >85% system memory
- **High CPU Usage**: >80% for 5 minutes

### Application-Specific Alerts
- **Study Session Failures**: >5% failure rate
- **Authentication Spike**: High auth failure rate
- **Token Limit Exceeded**: LLM token limits frequently hit

## 📈 Performance Optimization

### Using Metrics for Optimization

1. **OCR Service**:
   - Monitor confidence thresholds for optimal quality/speed balance
   - Track file size vs processing time correlation
   - Identify optimal preprocessing techniques

2. **LLM Service**:
   - Monitor token usage for cost optimization
   - Track generation time for user experience
   - Analyze error patterns for model improvement

3. **Backend Service**:
   - Identify slow endpoints for optimization
   - Monitor database query performance
   - Track user behavior patterns

## 🔧 Maintenance

### Regular Tasks

1. **Daily**: Check dashboard for anomalies
2. **Weekly**: Review alert patterns and adjust thresholds
3. **Monthly**: Analyze trends and plan optimizations

### Troubleshooting

```bash
# Check monitoring stack status
docker compose -f docker-compose.monitoring.yml ps

# View logs
docker compose -f docker-compose.monitoring.yml logs -f [service]

# Restart specific service
docker compose -f docker-compose.monitoring.yml restart [service]

# Rebuild with new metrics
docker compose build [service]
docker compose up -d [service]
```

## 🎯 For Stakeholders

### Business Value Metrics
- **User Experience**: Response times, error rates, success rates
- **Operational Efficiency**: Resource utilization, cost optimization
- **Quality Assurance**: OCR confidence, LLM generation quality
- **Reliability**: Uptime, error tracking, performance trends

### Reporting Capabilities
- **Real-time Dashboards**: Live system status
- **Historical Analysis**: Performance trends over time
- **Alert Notifications**: Proactive issue detection
- **Custom Metrics**: Business-specific KPIs

## 🔮 Future Enhancements

1. **Advanced ML Monitoring**: Model drift detection, A/B testing
2. **User Analytics**: Detailed user behavior tracking
3. **Cost Monitoring**: Resource cost analysis and optimization
4. **Predictive Alerting**: ML-based anomaly detection
5. **Custom Business Metrics**: KPI tracking and reporting

This monitoring stack provides comprehensive visibility into the entire Flashcards application, enabling proactive maintenance, performance optimization, and reliable operation.
