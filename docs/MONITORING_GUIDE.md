# Monitoring Guide

This guide covers the comprehensive monitoring setup for the flashcards application using Prometheus, Grafana, and MLflow.

## Overview

The monitoring stack includes:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **MLflow**: ML experiment tracking and model monitoring
- **AlertManager**: Alert management and notifications
- **cAdvisor**: Container metrics
- **Node Exporter**: System metrics
- **Redis Exporter**: Redis metrics

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Application   │───▶│   Prometheus    │───▶│     Grafana     │
│    Services     │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     MLflow      │    │  AlertManager   │    │   Dashboards    │
│   Tracking      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Service URLs

### Core Monitoring
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **AlertManager**: http://localhost:9093

### MLflow Tracking
- **OCR MLflow**: http://localhost:5000
- **LLM MLflow**: http://localhost:5001

### System Monitoring
- **cAdvisor**: http://localhost:8081
- **Node Exporter**: http://localhost:9100
- **Redis Exporter**: http://localhost:9121

### Application Services
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8002/docs
- **OCR API**: http://localhost:8000/docs
- **LLM API**: http://localhost:8001/docs

## Starting the Monitoring Stack

### Full Stack
```bash
# Start all services including monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### Application Only
```bash
# Start just the application services
docker-compose up -d
```

### Monitoring Only
```bash
# Start just the monitoring services
docker-compose -f docker-compose.monitoring.yml up -d
```

## Key Metrics

### Application Metrics

#### OCR Service
- `ocr_operations_total`: Total OCR operations by status and file type
- `ocr_processing_duration_seconds`: Processing time distribution
- `ocr_confidence_score`: Confidence score distribution
- `ocr_word_count`: Number of words extracted
- `ocr_filtered_words`: Words after confidence filtering
- `ocr_active_requests`: Currently active OCR requests

#### LLM Service
- `llm_generation_requests_total`: Total generation requests
- `llm_generation_duration_seconds`: Generation time distribution
- `llm_flashcards_generated_total`: Total flashcards generated
- `llm_active_generations`: Currently active generations
- `llm_generation_errors_total`: Generation errors by type

#### Backend Service
- `http_requests_total`: HTTP requests by method and status
- `http_request_duration_seconds`: Request duration distribution
- `flashcard_operations_total`: CRUD operations on flashcards
- `user_sessions_active`: Active user sessions

### System Metrics

#### Container Metrics (cAdvisor)
- CPU usage per container
- Memory usage per container
- Network I/O per container
- Disk I/O per container

#### System Metrics (Node Exporter)
- CPU usage and load average
- Memory usage and swap
- Disk usage and I/O
- Network interfaces

#### Redis Metrics
- Connected clients
- Memory usage
- Commands processed
- Key statistics

## Grafana Dashboards

### Pre-configured Dashboards

1. **Application Overview**
   - Service health status
   - Request rates and response times
   - Error rates and success rates

2. **OCR Service Dashboard**
   - OCR operation metrics
   - Confidence score analysis
   - File processing statistics
   - Performance trends

3. **LLM Service Dashboard**
   - Generation request metrics
   - Model performance
   - Response time analysis
   - Error tracking

4. **System Resources**
   - Container resource usage
   - System performance metrics
   - Redis performance

5. **MLflow Integration**
   - Experiment tracking overview
   - Model performance trends
   - Training metrics

### Custom Dashboard Creation

1. Access Grafana at http://localhost:3000
2. Login with admin/admin
3. Create new dashboard
4. Add panels with Prometheus queries
5. Configure alerts and notifications

## Alerting

### Alert Rules

#### Critical Alerts
- Service down (any application service)
- High error rate (>5% for 5 minutes)
- High response time (>5s for 5 minutes)
- Memory usage >90%
- Disk usage >85%

#### Warning Alerts
- Moderate error rate (>2% for 10 minutes)
- Elevated response time (>2s for 10 minutes)
- Memory usage >75%
- Disk usage >70%

### Alert Configuration

Edit `monitoring/alert_rules.yml` to customize alerts:

```yaml
groups:
  - name: application_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.instance }} is down"
```

## MLflow Integration

### OCR Service MLflow
- Comprehensive experiment tracking
- Confidence score analysis
- Performance optimization
- Error pattern analysis

### LLM Service MLflow
- Basic generation tracking
- Model performance monitoring
- Simple error logging
- Response time tracking

## Troubleshooting

### Common Issues

#### Prometheus Not Scraping Metrics
1. Check service discovery configuration
2. Verify metrics endpoints are accessible
3. Check Prometheus logs: `docker-compose logs prometheus`

#### Grafana Dashboard Not Loading
1. Verify Prometheus data source configuration
2. Check query syntax in panels
3. Ensure metrics are being collected

#### MLflow UI Not Accessible
1. Check MLflow container status
2. Verify port mappings
3. Check MLflow server logs

#### High Resource Usage
1. Monitor container resource limits
2. Check for memory leaks in applications
3. Optimize query frequency and retention

### Log Analysis

#### Application Logs
```bash
# View service logs
docker-compose logs -f ocr-service
docker-compose logs -f llm-service
docker-compose logs -f backend-service
```

#### Monitoring Logs
```bash
# View monitoring service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager
```

## Performance Optimization

### Metrics Collection
- Adjust scrape intervals based on needs
- Configure appropriate retention policies
- Use recording rules for complex queries

### Storage
- Monitor Prometheus storage usage
- Configure data retention policies
- Consider remote storage for long-term retention

### Alerting
- Fine-tune alert thresholds
- Implement alert fatigue prevention
- Use alert grouping and routing

## Best Practices

### Metrics Design
- Use consistent naming conventions
- Include relevant labels
- Avoid high cardinality metrics
- Document custom metrics

### Dashboard Design
- Focus on actionable metrics
- Use appropriate visualization types
- Include context and documentation
- Implement drill-down capabilities

### Alert Management
- Prioritize alerts by business impact
- Include runbook links in alerts
- Test alert delivery regularly
- Implement escalation procedures

## Security Considerations

### Access Control
- Secure Grafana with proper authentication
- Restrict Prometheus access
- Use HTTPS in production
- Implement role-based access

### Data Protection
- Sanitize sensitive data in metrics
- Secure MLflow experiment data
- Implement data retention policies
- Regular security audits

## Scaling Considerations

### High Availability
- Deploy Prometheus in HA mode
- Use Grafana clustering
- Implement load balancing
- Plan for disaster recovery

### Performance
- Optimize query performance
- Use federation for large deployments
- Implement metric aggregation
- Consider metric sampling

## Integration Examples

### Custom Metrics in Python Services
```python
from prometheus_client import Counter, Histogram, Gauge
import mlflow

# Prometheus metrics
REQUEST_COUNT = Counter('service_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('service_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('service_active_connections', 'Active connections')

# MLflow integration
@REQUEST_DURATION.time()
def process_request():
    with mlflow.start_run():
        mlflow.log_param("method", "POST")
        # Process request
        mlflow.log_metric("processing_time", duration)
```

### Alert Webhook Integration
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://backend-service:8002/alerts'
```
