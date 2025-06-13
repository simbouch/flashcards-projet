# 🎯 FlashCards AI - Intelligent Learning Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-orange.svg)](https://grafana.com/)
[![MLflow](https://img.shields.io/badge/MLflow-ML_Tracking-blue.svg)](https://mlflow.org/)

> Transform your documents into interactive flashcards using cutting-edge OCR and AI technology. Learn smarter, not harder with comprehensive monitoring and ML operations.

## 🌟 Overview

FlashCards AI is a modern, enterprise-grade full-stack application that revolutionizes the way you create and study flashcards. By leveraging advanced OCR (Optical Character Recognition) and AI technologies, it automatically extracts text from your documents and generates intelligent question-answer pairs for optimal learning. The platform includes comprehensive monitoring, ML operations tracking, and production-ready infrastructure.

### 🧠 Learning Methodology & Approach

FlashCards AI implements a scientifically-backed learning methodology that combines **spaced repetition**, **active recall**, and **AI-powered content generation** to maximize learning efficiency and retention:

#### **Spaced Repetition System**
- **Adaptive Review Scheduling**: Cards are automatically scheduled for review based on your performance, with difficult cards appearing more frequently
- **Forgetting Curve Optimization**: The system leverages Hermann Ebbinghaus's forgetting curve research to present cards at optimal intervals
- **Long-term Retention Focus**: Gradually increases intervals between reviews as you master content, moving knowledge from short-term to long-term memory

#### **Active Recall Learning**
- **Question-First Approach**: Forces your brain to actively retrieve information rather than passively reading
- **Immediate Feedback Loop**: Instant verification of answers reinforces correct knowledge and corrects misconceptions
- **Confidence-Based Progression**: Self-assessment options (Next, Review Later, Mastered) allow you to control the learning pace

#### **AI-Powered Question Generation**
- **Intelligent Content Analysis**: Advanced NLP algorithms analyze your documents to identify key concepts, facts, and relationships
- **Contextual Question Creation**: Generates questions that test understanding rather than mere memorization
- **Multiple Question Types**: Creates various question formats including factual recall, conceptual understanding, and application-based queries
- **Difficulty Calibration**: Automatically adjusts question complexity based on content depth and user progress

#### **Study Workflow & Progression**
1. **Document Processing**: Upload PDFs or images → OCR extracts text with high accuracy
2. **AI Analysis**: Machine learning models identify learning objectives and key information
3. **Smart Card Generation**: AI creates targeted question-answer pairs optimized for retention
4. **Adaptive Study Sessions**: Dynamic presentation based on your performance and confidence levels
5. **Progress Tracking**: Comprehensive analytics show mastery levels and learning velocity
6. **Continuous Optimization**: System learns from your interactions to improve future question generation

This methodology ensures that learners not only memorize information but develop deep understanding and long-lasting retention of the material.

### ✨ Key Features

#### 🤖 Core AI & Learning Features
- **AI-Powered Flashcard Generation** - Automatically create Q&A pairs from your documents using advanced NLP
- **Advanced OCR Processing** - Extract text from images and PDFs with high accuracy and confidence scoring
- **Interactive Study Mode** - Engaging flashcard interface with spaced repetition and progress tracking
- **Public Deck Sharing** - Browse and study community-created flashcard decks
- **Adaptive Learning** - Smart review scheduling based on performance and confidence levels

#### 📊 Monitoring & Operations
- **Comprehensive Monitoring** - Full observability with Prometheus, Grafana, and AlertManager
- **MLflow Integration** - Complete ML experiment tracking and model versioning
- **Real-time Metrics** - Live performance monitoring for all services and operations
- **Custom Dashboards** - Pre-built Grafana dashboards for application and system metrics
- **Intelligent Alerting** - Proactive notifications for system health and performance issues

#### 🏗️ Infrastructure & Security
- **Microservices Architecture** - Scalable, containerized services with Docker
- **Production-Ready** - Enterprise-grade infrastructure with health checks and auto-restart
- **Secure Authentication** - JWT-based security with user session management
- **Responsive Design** - Beautiful, modern UI that works on all devices
- **Easy Deployment** - One-command setup with Docker Compose

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[Vue.js 3 + Vuetify<br/>Port: 8080]
    end

    subgraph "API Gateway"
        API[FastAPI Backend<br/>Port: 8002]
    end

    subgraph "Core Services"
        OCR[OCR Service<br/>Tesseract + OpenCV<br/>Port: 8000]
        LLM[LLM Service<br/>AI Text Processing<br/>Port: 8001]
        DB[Database Service<br/>SQLite + SQLAlchemy]
    end

    subgraph "ML Operations"
        MLF_OCR[MLflow OCR<br/>Model Tracking<br/>Port: 5000]
        MLF_LLM[MLflow LLM<br/>Experiment Management<br/>Port: 5001]
    end

    subgraph "Monitoring Stack"
        PROM[Prometheus<br/>Metrics Collection<br/>Port: 9090]
        GRAF[Grafana<br/>Dashboards<br/>Port: 3000]
        ALERT[AlertManager<br/>Notifications<br/>Port: 9093]
        CADV[cAdvisor<br/>Container Metrics<br/>Port: 8081]
        NODE[Node Exporter<br/>System Metrics<br/>Port: 9100]
    end

    subgraph "Infrastructure"
        REDIS[Redis Cache<br/>Port: 6379]
        REDIS_EXP[Redis Exporter<br/>Port: 9121]
    end

    FE --> API
    API --> OCR
    API --> LLM
    API --> DB
    API --> REDIS
    OCR --> MLF_OCR
    LLM --> MLF_LLM

    PROM --> API
    PROM --> OCR
    PROM --> LLM
    PROM --> CADV
    PROM --> NODE
    PROM --> REDIS_EXP
    GRAF --> PROM
    ALERT --> PROM
```

### 🔧 Technology Stack

#### Frontend Layer
- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vuetify 3** - Material Design component library with modern theming
- **Pinia** - State management with TypeScript support
- **Vue Router** - Client-side routing with navigation guards
- **Axios** - HTTP client with interceptors and error handling

#### Backend Services
- **FastAPI** - Modern Python web framework with automatic API documentation
- **SQLAlchemy** - Database ORM with migration support
- **Pydantic** - Data validation and serialization
- **JWT** - Secure authentication with refresh tokens
- **Redis** - High-performance caching and session storage

#### AI/ML Pipeline
- **Tesseract OCR** - Advanced text extraction with confidence scoring
- **OpenCV** - Computer vision and image preprocessing
- **MLflow** - Complete ML lifecycle management and experiment tracking
- **Transformers** - State-of-the-art NLP models for text processing
- **Loguru** - Structured logging for debugging and monitoring

#### Monitoring & Observability
- **Prometheus** - Metrics collection and time-series database
- **Grafana** - Visualization dashboards and alerting
- **AlertManager** - Intelligent alert routing and notifications
- **cAdvisor** - Container resource monitoring
- **Node Exporter** - System-level metrics collection
- **Redis Exporter** - Redis performance monitoring

#### Infrastructure & DevOps
- **Docker** - Containerization with multi-stage builds
- **Docker Compose** - Service orchestration and networking
- **Nginx** - Reverse proxy and static file serving
- **SQLite** - Lightweight database for development
- **Health Checks** - Automated service health monitoring

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git
- 4GB+ RAM recommended

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/simbouch/flashcards-projet.git
   cd flashcards-projet
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**

   #### 🌐 Core Application Services
   - **Frontend Application**: [http://localhost:8080](http://localhost:8080)
   - **Backend API Documentation**: [http://localhost:8002/docs](http://localhost:8002/docs)
   - **OCR Service API**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **LLM Service API**: [http://localhost:8001/docs](http://localhost:8001/docs)

   #### 📊 ML Operations & Tracking
   - **MLflow OCR Tracking**: [http://localhost:5000](http://localhost:5000)
   - **MLflow LLM Tracking**: [http://localhost:5001](http://localhost:5001)

   #### 🔍 Monitoring & Observability
   - **Grafana Dashboards**: [http://localhost:3000](http://localhost:3000) (admin/flashcards2024)
   - **Prometheus Metrics**: [http://localhost:9090](http://localhost:9090)
   - **AlertManager**: [http://localhost:9093](http://localhost:9093)
   - **cAdvisor Container Metrics**: [http://localhost:8081](http://localhost:8081)
   - **Node Exporter System Metrics**: [http://localhost:9100](http://localhost:9100)
   - **Redis Metrics**: [http://localhost:9121](http://localhost:9121)

### First Steps

1. **Create an account** at [http://localhost:8080/register](http://localhost:8080/register)
2. **Upload a document** (PDF or image) in the Documents section
3. **Generate flashcards** from your uploaded document
4. **Start studying** with the interactive study mode
5. **Monitor performance** via [Grafana dashboards](http://localhost:3000)

## 📊 Comprehensive Monitoring & Observability

FlashCards AI includes a complete monitoring stack for production-ready observability, performance tracking, and proactive alerting.

### 🚀 Quick Monitoring Setup

#### Start with Full Monitoring
```bash
# Start all services including monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

#### Application Only
```bash
# Start just the core application services
docker-compose up -d
```

#### Monitoring Only
```bash
# Start just the monitoring infrastructure
docker-compose -f docker-compose.monitoring.yml up -d
```

### 🎯 Monitoring Architecture & Data Flow

The monitoring system follows a comprehensive observability pattern:

1. **Metrics Collection**: Prometheus scrapes metrics from all services every 15 seconds
2. **Data Storage**: Time-series data stored in Prometheus with 200-hour retention
3. **Visualization**: Grafana provides real-time dashboards and historical analysis
4. **Alerting**: AlertManager handles intelligent alert routing and notifications
5. **ML Tracking**: MLflow tracks experiment data and model performance

### 📈 Key Metrics & KPIs

#### 🤖 OCR Service Metrics
- **Processing Performance**: `ocr_processing_duration_seconds` - OCR operation latency
- **Quality Metrics**: `ocr_confidence_score` - Text extraction confidence distribution
- **Throughput**: `ocr_operations_total` - Total operations by status and file type
- **Resource Usage**: `ocr_active_requests` - Concurrent processing load
- **Data Quality**: `ocr_word_count` vs `ocr_filtered_words` - Confidence filtering effectiveness

#### 🧠 LLM Service Metrics
- **Generation Performance**: `llm_generation_duration_seconds` - AI processing time
- **Output Quality**: `llm_flashcards_generated_total` - Successful flashcard creation
- **System Load**: `llm_active_generations` - Concurrent AI operations
- **Error Tracking**: `llm_generation_errors_total` - Failure analysis by type
- **Model Performance**: Response quality and consistency metrics

#### 🌐 Backend API Metrics
- **Request Performance**: `http_request_duration_seconds` - API response times
- **Traffic Analysis**: `http_requests_total` - Request volume by endpoint and status
- **Business Metrics**: `flashcard_operations_total` - CRUD operations tracking
- **User Activity**: `user_sessions_active` - Concurrent user sessions
- **Database Performance**: Query execution times and connection pool usage

#### 🖥️ System & Infrastructure Metrics
- **Container Health**: CPU, memory, network, and disk I/O per service
- **System Resources**: Host-level CPU, memory, disk usage, and network interfaces
- **Redis Performance**: Connection count, memory usage, command throughput
- **Service Availability**: Health check status and uptime tracking

### 📊 Pre-Built Grafana Dashboards

Access comprehensive dashboards at [http://localhost:3000](http://localhost:3000) (admin/flashcards2024):

#### 1. **Application Overview Dashboard**
- Service health status and availability
- Request rates, response times, and error rates
- Real-time performance metrics across all services
- Business KPIs and user activity tracking

#### 2. **OCR Service Performance Dashboard**
- OCR operation metrics and processing times
- Confidence score analysis and quality trends
- File processing statistics by type and size
- Error pattern analysis and troubleshooting

#### 3. **LLM Service Intelligence Dashboard**
- AI generation request metrics and performance
- Model response time analysis and optimization
- Flashcard generation success rates
- Resource utilization and scaling insights

#### 4. **System Resources Dashboard**
- Container resource usage (CPU, memory, network, disk)
- Host system performance metrics
- Redis performance and caching effectiveness
- Infrastructure health and capacity planning

#### 5. **MLflow Integration Dashboard**
- Experiment tracking overview and trends
- Model performance comparison
- Training metrics and optimization insights
- ML pipeline health and data quality

### 🚨 Intelligent Alerting System

#### Critical Alerts (Immediate Response Required)
- **Service Down**: Any application service becomes unavailable
- **High Error Rate**: >5% error rate sustained for 5+ minutes
- **Severe Performance Degradation**: >5s response time for 5+ minutes
- **Resource Exhaustion**: Memory usage >90% or disk usage >85%

#### Warning Alerts (Monitoring Required)
- **Elevated Error Rate**: >2% error rate for 10+ minutes
- **Performance Issues**: >2s response time for 10+ minutes
- **Resource Pressure**: Memory >75% or disk >70%
- **ML Model Drift**: Significant performance degradation in AI services

### 🔧 MLflow ML Operations Integration

#### OCR Service MLflow (Comprehensive Tracking)
- **Experiment Management**: Complete OCR operation tracking
- **Performance Analytics**: Confidence score analysis and optimization
- **Quality Metrics**: Text extraction accuracy and error pattern analysis
- **Model Versioning**: OCR model updates and A/B testing

#### LLM Service MLflow (Streamlined Tracking)
- **Generation Monitoring**: Basic AI operation tracking
- **Performance Metrics**: Response time and quality monitoring
- **Error Analysis**: Simple failure pattern detection
- **Resource Tracking**: Model resource usage optimization

## 📖 User Guide

### Step-by-Step Workflow

#### 1. 📤 Upload Documents
- Navigate to the **Documents** section
- Upload PDF files or images (JPG, PNG)
- Provide a descriptive name for your document
- Wait for OCR processing to complete

#### 2. 🎯 Generate Flashcards
- Go to **My Decks** and click **Create Deck**
- Select a processed document as the source
- Choose whether to make the deck public
- AI will automatically generate question-answer pairs

#### 3. 📚 Study Mode
- Click **Study** on any deck to enter study mode
- **Tap cards** to flip between questions and answers
- Use study controls:
  - **Next**: Move card behind the next one
  - **Review Later**: Send to end of deck (2nd time removes)
  - **Mastered**: Remove from current session
  - **End Session**: Quit and save progress

#### 4. 🌐 Explore Public Decks
- Browse community-created flashcard decks
- Study public decks without creating an account
- Get inspired by other learners' content

## 🛠️ Development

### 🏗️ Complete Project Structure

```
flashcards-ai/
├── 🎨 frontend_service/              # Vue.js 3 + Vuetify Frontend (Port: 8080)
│   ├── src/
│   │   ├── components/               # Reusable Vue components
│   │   ├── views/                   # Page components (modernized UI)
│   │   ├── store/                   # Pinia state management
│   │   ├── assets/                  # Static assets and modern styles
│   │   └── router/                  # Vue Router configuration
│   ├── public/                      # Static public assets
│   ├── Dockerfile                   # Frontend container configuration
│   └── nginx.conf                   # Nginx reverse proxy config
│
├── 🚀 backend_service/              # FastAPI Backend API (Port: 8002)
│   ├── src/
│   │   ├── api/                     # RESTful API endpoints
│   │   ├── models/                  # SQLAlchemy database models
│   │   ├── services/                # Business logic layer
│   │   ├── core/                    # Configuration and utilities
│   │   └── auth/                    # JWT authentication system
│   ├── tests/                       # Comprehensive test suite
│   ├── uploads/                     # Document upload storage
│   └── Dockerfile                   # Backend container configuration
│
├── 👁️ ocr_service/                  # OCR Processing Service (Port: 8000)
│   ├── src/
│   │   ├── ocr_engine.py           # Tesseract OCR integration
│   │   ├── image_processor.py      # OpenCV image preprocessing
│   │   ├── confidence_filter.py    # Quality control and filtering
│   │   └── metrics.py              # Prometheus metrics collection
│   ├── tests/                       # OCR-specific tests
│   ├── demo_images/                 # Test images for development
│   └── mlruns/                      # Local MLflow tracking data
│
├── 🧠 llm_service/                  # AI Text Processing Service (Port: 8001)
│   ├── src/
│   │   ├── llm_engine.py           # AI model integration
│   │   ├── flashcard_generator.py  # Q&A pair generation
│   │   ├── text_processor.py       # NLP preprocessing
│   │   └── metrics.py              # Performance monitoring
│   ├── models/                      # AI model storage
│   └── tests/                       # LLM service tests
│
├── 🗄️ db_module/                    # Database Service & Models
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── database.py                  # Database connection management
│   ├── crud.py                      # Database operations
│   ├── migrations/                  # Alembic database migrations
│   └── data/                        # SQLite database storage
│
├── 📊 mlflow/                       # ML Operations Tracking
│   ├── Dockerfile.ocr               # OCR MLflow server (Port: 5000)
│   ├── Dockerfile.llm               # LLM MLflow server (Port: 5001)
│   └── start.sh                     # MLflow startup scripts
│
├── 📈 monitoring/                   # Comprehensive Monitoring Stack
│   ├── prometheus.yml               # Prometheus configuration
│   ├── alert_rules.yml             # Alerting rules and thresholds
│   ├── alertmanager.yml            # Alert routing and notifications
│   └── grafana/
│       ├── provisioning/            # Automated dashboard provisioning
│       └── dashboards/              # Pre-built monitoring dashboards
│
├── 🧪 tests/                        # Comprehensive Test Suite
│   ├── unit/                        # Unit tests for all services
│   ├── integration/                 # Integration and API tests
│   ├── conftest.py                  # Pytest configuration
│   └── README.md                    # Testing documentation
│
├── 📚 docs/                         # Documentation
│   ├── database_schema.md           # Database design documentation
│   ├── database_mcd.md             # Conceptual data model
│   └── database_mpd.md             # Physical data model
│
├── 🔧 Configuration Files
│   ├── docker-compose.yml           # Core application services
│   ├── docker-compose.monitoring.yml # Monitoring stack services
│   ├── pytest.ini                   # Test configuration
│   └── .env.example                 # Environment variables template
│
├── 📋 Documentation & Guides
│   ├── README.md                    # This comprehensive guide
│   ├── MONITORING_GUIDE.md          # Detailed monitoring documentation
│   ├── MLflow_Demo_Guide.md         # ML operations walkthrough
│   ├── SECURITY.md                  # Security best practices
│   ├── PRIVACY.md                   # Privacy policy and data handling
│   └── LICENSE                      # MIT license
│
└── 🚀 Deployment & Render Files
    ├── Dockerfile.render             # Render.com frontend deployment
    ├── Dockerfile.render.backend     # Render.com backend deployment
    ├── render-build.sh              # Render build script
    ├── render-start.sh              # Render startup script
    └── render-deployment-guide.md   # Render deployment instructions
```

### Local Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/simbouch/flashcards-projet.git
   cd flashcards-projet
   ```

2. **Environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

### Running Tests

```bash
# Frontend tests
cd frontend_service
npm run test

# Backend tests
cd backend_service
pytest

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Run tests by category
pytest -m auth
pytest -m decks
pytest -m flashcards
pytest -m study
pytest -m unit
pytest -m integration
```

## 📊 Comprehensive API Documentation

### 🌐 Service Endpoints Overview

#### Core Application APIs
- **Backend API**: [http://localhost:8002/docs](http://localhost:8002/docs) - Complete FastAPI documentation
- **OCR Service**: [http://localhost:8000/docs](http://localhost:8000/docs) - OCR processing endpoints
- **LLM Service**: [http://localhost:8001/docs](http://localhost:8001/docs) - AI text processing endpoints

### 🔐 Authentication & User Management

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | `/auth/register` | Create new user account | User profile + JWT tokens |
| POST | `/auth/login` | Authenticate user credentials | Access + refresh tokens |
| POST | `/auth/refresh` | Refresh access token | New access token |
| POST | `/auth/logout` | Invalidate user session | Success confirmation |
| GET | `/auth/me` | Get current user profile | User details |
| PUT | `/auth/profile` | Update user profile | Updated profile |

### 📄 Document Management & Processing

| Method | Endpoint | Description | Processing Flow |
|--------|----------|-------------|-----------------|
| GET | `/documents/` | List user documents | Returns paginated document list |
| POST | `/documents/upload` | Upload PDF/image document | OCR → Text extraction → Storage |
| GET | `/documents/{id}` | Get document details | Document metadata + extracted text |
| GET | `/documents/{id}/text` | Get extracted text | Raw OCR output with confidence |
| DELETE | `/documents/{id}` | Delete document | Removes file + database record |
| GET | `/documents/{id}/status` | Check processing status | Real-time processing updates |

### 🎯 Flashcard & Deck Operations

| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| GET | `/decks/` | List user decks | Pagination, filtering, sorting |
| POST | `/decks/` | Create new deck | Manual or AI-generated from document |
| GET | `/decks/{id}` | Get deck with flashcards | Complete deck data + cards |
| PUT | `/decks/{id}` | Update deck metadata | Title, description, visibility |
| DELETE | `/decks/{id}` | Delete deck | Cascades to all flashcards |
| GET | `/decks/public` | List public decks | Community-shared content |
| POST | `/decks/{id}/clone` | Clone public deck | Copy to personal collection |
| GET | `/decks/{id}/flashcards` | Get deck flashcards | Paginated card list |
| POST | `/decks/{id}/flashcards` | Add flashcard to deck | Manual card creation |
| PUT | `/flashcards/{id}` | Update flashcard | Edit question/answer |
| DELETE | `/flashcards/{id}` | Delete flashcard | Remove from deck |

### 📚 Study Session & Progress Tracking

| Method | Endpoint | Description | Analytics |
|--------|----------|-------------|-----------|
| POST | `/study/sessions` | Start study session | Creates session with deck |
| GET | `/study/sessions/{id}` | Get session details | Current progress + cards |
| POST | `/study/sessions/{id}/records` | Record study response | Tracks performance + timing |
| PUT | `/study/sessions/{id}/end` | End study session | Saves final statistics |
| GET | `/study/history` | Get study history | Performance trends + analytics |
| GET | `/study/stats` | Get study statistics | Personal learning metrics |
| GET | `/study/progress/{deck_id}` | Get deck progress | Mastery levels per card |

### 🤖 AI & ML Service Endpoints

#### OCR Service (Port 8000)
| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| POST | `/ocr/process` | Process image/PDF | Text extraction + confidence |
| GET | `/ocr/health` | Service health check | Status + performance metrics |
| GET | `/ocr/metrics` | Prometheus metrics | OCR performance data |

#### LLM Service (Port 8001)
| Method | Endpoint | Description | Features |
|--------|----------|-------------|----------|
| POST | `/llm/generate` | Generate flashcards | AI-powered Q&A creation |
| POST | `/llm/analyze` | Analyze text content | Content structure analysis |
| GET | `/llm/health` | Service health check | Model status + metrics |
| GET | `/llm/metrics` | Prometheus metrics | AI performance data |

### 📊 Monitoring & Health Endpoints

| Method | Endpoint | Description | Data |
|--------|----------|-------------|------|
| GET | `/health` | Application health | Service status + dependencies |
| GET | `/metrics` | Prometheus metrics | Performance + business metrics |
| GET | `/info` | Service information | Version + configuration |

### 🔧 Advanced Features

#### Batch Operations
- **Bulk Upload**: Process multiple documents simultaneously
- **Batch Generation**: Create flashcards from multiple sources
- **Export/Import**: Backup and restore deck collections

#### Real-time Features
- **WebSocket Updates**: Live processing status updates
- **Progress Streaming**: Real-time study session progress
- **Notification System**: Alert users of completed processing

#### API Rate Limiting
- **Authentication Required**: All endpoints except public decks
- **Rate Limits**: 100 requests/minute per user
- **Bulk Limits**: Special limits for batch operations

For complete interactive API documentation with request/response examples, visit:
- **Backend API**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **OCR Service**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **LLM Service**: [http://localhost:8001/docs](http://localhost:8001/docs)

## 🚨 Comprehensive Troubleshooting Guide

### 🔧 Common Issues & Solutions

#### 🚀 Application Startup Issues

**Problem**: Services won't start or fail during initialization
```bash
# Check Docker system status
docker --version && docker-compose --version
docker system df  # Check disk space
docker system prune  # Clean up unused resources

# Complete rebuild with fresh containers
docker-compose down -v --remove-orphans
docker-compose up --build --force-recreate

# Check service health status
docker-compose ps
docker-compose logs --tail=50 [service-name]
```

**Problem**: Port conflicts or binding errors
```bash
# Check port usage
netstat -tulpn | grep -E ':(8080|8002|8000|8001|5000|5001|3000|9090)'

# Kill processes using required ports
sudo lsof -ti:8080 | xargs kill -9  # Replace 8080 with conflicting port
```

#### 🤖 OCR Service Issues

**Problem**: OCR processing fails or returns poor results
```bash
# Check OCR service health and logs
docker-compose logs -f ocr-service
curl http://localhost:8000/health

# Verify Tesseract installation and language packs
docker-compose exec ocr-service tesseract --version
docker-compose exec ocr-service tesseract --list-langs

# Test OCR with sample image
docker-compose exec ocr-service python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
"
```

**Problem**: Low confidence scores or poor text extraction
- Ensure images are high resolution (300+ DPI)
- Check image preprocessing in OCR service logs
- Verify document language matches Tesseract language packs
- Monitor confidence thresholds in MLflow dashboard

#### 🧠 LLM Service Issues

**Problem**: AI flashcard generation fails or produces poor quality
```bash
# Check LLM service status and resource usage
docker-compose logs -f llm-service
docker stats llm-service

# Verify model loading
curl http://localhost:8001/health
```

**Problem**: Out of memory errors in LLM service
```bash
# Increase memory allocation in docker-compose.yml
# Current limit: 4GB, try increasing to 6GB or 8GB
docker-compose down
# Edit docker-compose.yml LLM service memory limits
docker-compose up -d llm-service
```

#### 🗄️ Database & Storage Issues

**Problem**: Database connection errors or corruption
```bash
# Reset database completely
docker-compose down -v
rm -rf db_module/data/*  # WARNING: This deletes all data
docker-compose up --build

# Check database integrity
docker-compose exec db-service sqlite3 /app/data/flashcards.db ".schema"
```

**Problem**: Upload failures or storage issues
```bash
# Check upload directory permissions
ls -la uploads/
chmod 755 uploads/

# Monitor disk space
df -h
docker system df
```

#### 📊 Monitoring Stack Issues

**Problem**: Grafana dashboards not loading or showing no data
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify Grafana data source
curl -u admin:flashcards2024 http://localhost:3000/api/datasources

# Restart monitoring stack
docker-compose -f docker-compose.monitoring.yml down
docker-compose -f docker-compose.monitoring.yml up -d
```

**Problem**: Metrics not being collected
```bash
# Check service metrics endpoints
curl http://localhost:8002/metrics  # Backend
curl http://localhost:8000/metrics  # OCR
curl http://localhost:8001/metrics  # LLM

# Verify Prometheus configuration
docker-compose exec prometheus cat /etc/prometheus/prometheus.yml
```

### ⚡ Performance Optimization

#### 🖥️ System Requirements & Tuning
- **Memory**: Minimum 8GB RAM, recommended 16GB+ for optimal performance
- **CPU**: Multi-core processor recommended for concurrent AI processing
- **Storage**: SSD recommended, ensure 10GB+ free space for documents and models
- **Docker**: Allocate 6GB+ memory to Docker Desktop

#### 🚀 Service-Specific Optimizations

**OCR Service Performance**
```bash
# Monitor OCR processing times
curl http://localhost:5000  # Check MLflow OCR metrics

# Optimize image preprocessing
# - Resize large images before processing
# - Use appropriate image formats (PNG for text, JPEG for photos)
# - Ensure good contrast and resolution
```

**LLM Service Performance**
```bash
# Monitor AI generation performance
curl http://localhost:5001  # Check MLflow LLM metrics

# Optimize model performance
# - Adjust batch sizes in LLM configuration
# - Monitor GPU usage if available
# - Consider model quantization for faster inference
```

**Database Performance**
```bash
# Monitor database performance
docker-compose exec db-service sqlite3 /app/data/flashcards.db "
.timer on
.stats on
SELECT COUNT(*) FROM flashcards;
"

# Optimize database
# - Regular VACUUM operations
# - Index optimization
# - Query performance monitoring
```

#### 🌐 Network & Caching Optimization
- **Redis Configuration**: Monitor cache hit rates and memory usage
- **Network Latency**: Use local deployment for development
- **CDN Integration**: Consider CDN for static assets in production

### 📊 Monitoring & Diagnostics

#### 🔍 Health Check Commands
```bash
# Comprehensive health check
./scripts/health_check.sh  # If available

# Manual service verification
curl http://localhost:8080  # Frontend
curl http://localhost:8002/health  # Backend
curl http://localhost:8000/health  # OCR
curl http://localhost:8001/health  # LLM
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy  # Prometheus
```

#### 📈 Performance Monitoring
```bash
# Real-time resource monitoring
docker stats

# Service-specific monitoring
docker-compose logs -f --tail=100 [service-name]

# Check MLflow experiments
open http://localhost:5000  # OCR MLflow
open http://localhost:5001  # LLM MLflow
```

#### 🚨 Alert Investigation
```bash
# Check AlertManager status
curl http://localhost:9093/api/v1/alerts

# View Prometheus alerts
curl http://localhost:9090/api/v1/alerts

# Grafana alert history
# Access via Grafana UI at http://localhost:3000
```

### 🆘 Emergency Recovery Procedures

#### 🔄 Complete System Reset
```bash
# Nuclear option: Complete reset (DESTROYS ALL DATA)
docker-compose down -v --remove-orphans
docker system prune -a --volumes
docker-compose up --build
```

#### 💾 Data Backup & Recovery
```bash
# Backup critical data
cp -r db_module/data/ backup_$(date +%Y%m%d)/
cp -r uploads/ backup_uploads_$(date +%Y%m%d)/

# Restore from backup
docker-compose down
cp -r backup_20240101/data/ db_module/
cp -r backup_uploads_20240101/ uploads/
docker-compose up -d
```

### 📞 Getting Help

#### 🐛 Bug Reports
1. Check existing issues on GitHub
2. Gather system information: `docker-compose logs > debug.log`
3. Include steps to reproduce the issue
4. Provide relevant error messages and logs

#### 💡 Feature Requests
1. Search existing feature requests
2. Describe the use case and expected behavior
3. Consider contributing via pull request

#### 📚 Additional Resources
- **Monitoring Guide**: [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- **MLflow Demo**: [MLflow_Demo_Guide.md](MLflow_Demo_Guide.md)
- **Security Guide**: [SECURITY.md](SECURITY.md)
- **API Documentation**: [http://localhost:8002/docs](http://localhost:8002/docs)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction
- [Vue.js](https://vuejs.org/) and [Vuetify](https://vuetifyjs.com/) for the beautiful frontend
- [FastAPI](https://fastapi.tiangolo.com/) for the robust backend framework
- [MLflow](https://mlflow.org/) for ML experiment tracking

## 🌟 Production Deployment

### 🚀 Render.com Deployment
FlashCards AI is production-ready and can be deployed to Render.com using the provided configuration files:

- **Frontend Deployment**: Uses `Dockerfile.render` for optimized Vue.js build
- **Backend Deployment**: Uses `Dockerfile.render.backend` for FastAPI service
- **Deployment Guide**: See [render-deployment-guide.md](render-deployment-guide.md) for complete instructions

### 🔧 Environment Configuration
```bash
# Production environment variables
NODE_ENV=production
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
JWT_SECRET_KEY=your-secure-secret-key
CORS_ORIGINS=https://your-domain.com
```

### 📊 Production Monitoring
- Configure external monitoring services (DataDog, New Relic)
- Set up log aggregation (ELK Stack, Splunk)
- Implement external alerting (PagerDuty, Slack)
- Use managed databases (PostgreSQL, Redis Cloud)

## 🏆 Key Achievements & Features

### 🎯 Technical Excellence
- **100% Containerized**: All services run in Docker with health checks
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage
- **Production Monitoring**: Full observability with Prometheus and Grafana
- **ML Operations**: Complete MLflow integration for AI model tracking
- **Modern UI/UX**: Professional Vue.js 3 interface with Vuetify 3

### 📈 Performance & Scalability
- **High Availability**: Auto-restart policies and health monitoring
- **Efficient Processing**: Optimized OCR and AI processing pipelines
- **Caching Strategy**: Redis-based caching for improved performance
- **Resource Management**: Proper memory and CPU limits for all services
- **Monitoring Alerts**: Proactive alerting for system health and performance

### 🔒 Security & Compliance
- **JWT Authentication**: Secure token-based authentication system
- **Data Privacy**: GDPR-compliant data handling and user privacy
- **Input Validation**: Comprehensive input sanitization and validation
- **Security Headers**: Proper CORS and security header configuration
- **Audit Logging**: Complete audit trail for all user actions

## 👨‍💻 Developer & Project Information

### 🧑‍💻 Lead Developer
**Bouchaib Khribech** - Full-Stack Developer & AI Engineer

🌐 **Portfolio**: [khribech-b.vercel.app](https://khribech-b.vercel.app/)
📧 **Contact**: [simplonbouchaib@gmail.com](mailto:simplonbouchaib@gmail.com)
💼 **LinkedIn**: [Connect on LinkedIn](https://linkedin.com/in/bouchaib-khribech)

### 🎯 Expertise & Passion
Passionate about AI, machine learning, and creating innovative educational technology solutions that make learning more effective and accessible. Specialized in:

- **Full-Stack Development**: Vue.js, FastAPI, Python, JavaScript
- **AI/ML Engineering**: OCR, NLP, MLflow, Model Deployment
- **DevOps & Monitoring**: Docker, Prometheus, Grafana, CI/CD
- **Educational Technology**: Learning methodologies, UX/UI design

### 🏗️ Project Architecture Philosophy
This project demonstrates enterprise-grade software development practices:
- **Microservices Architecture**: Scalable, maintainable service design
- **Observability First**: Comprehensive monitoring and logging
- **Test-Driven Development**: Extensive test coverage and quality assurance
- **User-Centric Design**: Focus on learning effectiveness and user experience

### 📊 Project Statistics
- **Services**: 10+ containerized microservices
- **Languages**: Python, JavaScript, SQL, YAML
- **Frameworks**: Vue.js 3, FastAPI, SQLAlchemy, Vuetify 3
- **Infrastructure**: Docker, Prometheus, Grafana, MLflow, Redis
- **Testing**: 95%+ code coverage with comprehensive test suite

---

<div align="center">
  <h3>🎓 FlashCards AI - Revolutionizing Digital Learning</h3>
  <p>Made with ❤️ and cutting-edge technology</p>
  <p>
    <a href="https://github.com/simbouch/flashcards-projet">⭐ Star us on GitHub</a> •
    <a href="https://github.com/simbouch/flashcards-projet/issues">🐛 Report Bug</a> •
    <a href="https://github.com/simbouch/flashcards-projet/issues">💡 Request Feature</a> •
    <a href="https://khribech-b.vercel.app/">🌐 Developer Portfolio</a>
  </p>

  <p><strong>Transform your learning experience with AI-powered flashcards!</strong></p>
</div>
