# Flashcards Application

A full-stack platform for automatic flashcard generation from PDFs/images. The application uses OCR with Tesseract to extract text from images, generates question-answer pairs using a locally fine-tuned French LLM, stores data in SQLite, provides a FastAPI REST API with authentication, and offers a Vue.js review UI.

## Features

- **OCR Processing**: Extract text from images and PDFs using Tesseract OCR
- **AI-Generated Flashcards**: Automatically generate question-answer pairs from extracted text
- **User Management**: Register, login, and manage user profiles
- **Document Management**: Upload, process, and manage documents
- **Flashcard Decks**: Create, edit, and share flashcard decks
- **Study System**: Review flashcards with a spaced repetition system
- **Responsive UI**: Modern Vue.js interface that works on desktop and mobile
- **Security**: JWT authentication, password hashing, and CSRF protection
- **GDPR Compliance**: User data export and deletion options

## Architecture

The application follows a microservices architecture with the following components:

- **OCR Service**: Extracts text from images using Tesseract
- **LLM Service**: Generates flashcards from text using a language model
- **Database Module**: Handles data storage and retrieval
- **Backend Service**: Provides the main API and coordinates between services
- **Frontend Service**: Delivers the user interface

## Technologies

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **Frontend**: Vue.js, Vuetify, Pinia
- **Database**: SQLite
- **AI/ML**: Transformers, PyTorch
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Testing**: Pytest, Vue Test Utils

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/simbouch/flashcards-projet.git
   cd flashcards-projet
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Start the application using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost:8080

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run tests by category
pytest -m auth
pytest -m decks
pytest -m flashcards
pytest -m study
pytest -m unit
pytest -m integration

# Run tests for specific services
pytest backend_service/tests
pytest db_module/tests
pytest ocr_service/tests
pytest llm_service/tests

# Run frontend tests
cd frontend_service
npm run test:unit
```

### Test Structure

The tests are organized as follows:

- `tests/`: Application-level tests
  - `integration/`: Integration tests for the entire application
  - `unit/`: Unit tests for application components

- `backend_service/tests/`: Backend service tests
  - `unit/`: Unit tests for backend service components
  - `integration/`: Integration tests for backend service components

- `db_module/tests/`: Database module tests
- `ocr_service/tests/`: OCR service tests
- `llm_service/tests/`: LLM service tests

### Building Docker Images

```bash
docker-compose build
```

## Documentation

- [Privacy Policy](PRIVACY.md)
- [Security Policy](SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
