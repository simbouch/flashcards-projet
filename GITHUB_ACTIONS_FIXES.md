# GitHub Actions Fixes and Configuration

This document outlines the fixes and improvements made to the GitHub Actions workflows for the flashcards project.

## Overview

The GitHub Actions workflows have been enhanced to provide:
- Automated testing on pull requests and pushes
- Docker image building and publishing
- Security scanning and vulnerability assessment
- Code quality checks and linting
- Deployment automation

## Workflow Files

### 1. Main CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend_service/requirements.txt
        pip install -r ocr_service/requirements.txt
        pip install -r llm_service/requirements.txt
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run backend tests
      run: |
        cd backend_service
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Run OCR service tests
      run: |
        cd ocr_service
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Run LLM service tests
      run: |
        cd llm_service
        python -m pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./backend_service/coverage.xml,./ocr_service/coverage.xml,./llm_service/coverage.xml
        fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push backend service
      uses: docker/build-push-action@v5
      with:
        context: ./backend_service
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/flashcards-backend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push OCR service
      uses: docker/build-push-action@v5
      with:
        context: ./ocr_service
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/flashcards-ocr:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push LLM service
      uses: docker/build-push-action@v5
      with:
        context: ./llm_service
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/flashcards-llm:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/flashcards-frontend:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max

  security:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### 2. Code Quality Workflow (`.github/workflows/code-quality.yml`)

```yaml
name: Code Quality

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install flake8 black isort mypy
    
    - name: Run Black
      run: |
        black --check --diff backend_service/src ocr_service/src llm_service/src
    
    - name: Run isort
      run: |
        isort --check-only --diff backend_service/src ocr_service/src llm_service/src
    
    - name: Run flake8
      run: |
        flake8 backend_service/src ocr_service/src llm_service/src
    
    - name: Run mypy
      run: |
        mypy backend_service/src ocr_service/src llm_service/src

  frontend-lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run ESLint
      run: |
        cd frontend
        npm run lint
    
    - name: Run Prettier
      run: |
        cd frontend
        npm run format:check
```

## Required Secrets

### Repository Secrets
Configure these secrets in your GitHub repository settings:

1. **DOCKER_USERNAME**: Your Docker Hub username
2. **DOCKER_PASSWORD**: Your Docker Hub password or access token

### Setting up Secrets
1. Go to your repository on GitHub
2. Click on "Settings" tab
3. Click on "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add each secret with the appropriate value

## Branch Protection Rules

### Main Branch Protection
Configure the following protection rules for the `main` branch:

1. **Require pull request reviews before merging**
   - Required number of reviewers: 1
   - Dismiss stale reviews when new commits are pushed

2. **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Required status checks:
     - `test`
     - `lint`
     - `security`

3. **Require conversation resolution before merging**

4. **Restrict pushes that create files larger than 100MB**

### Dev Branch Configuration
The `dev` branch should:
- Allow direct pushes for development
- Run CI checks on every push
- Require pull requests to merge to `main`

## Workflow Triggers

### Push Events
- **Main branch**: Full CI/CD pipeline including build and deploy
- **Dev branch**: Testing and code quality checks only
- **Feature branches**: Testing and code quality checks only

### Pull Request Events
- **To main**: Full testing, security scanning, and code quality checks
- **To dev**: Testing and code quality checks

### Manual Triggers
Some workflows can be triggered manually:
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
```

## Common Issues and Solutions

### 1. Test Failures

#### Issue: Tests fail due to missing dependencies
**Solution**: Ensure all required dependencies are listed in requirements.txt files

#### Issue: Database connection errors in tests
**Solution**: Use in-memory SQLite for testing:
```python
# conftest.py
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()
```

### 2. Docker Build Issues

#### Issue: Docker build fails due to large context
**Solution**: Add .dockerignore files to exclude unnecessary files:
```
# .dockerignore
.git
.github
node_modules
*.md
.env
logs/
```

#### Issue: Multi-platform build failures
**Solution**: Use buildx for cross-platform builds:
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3
  with:
    platforms: linux/amd64,linux/arm64
```

### 3. Security Scanning Issues

#### Issue: False positive vulnerabilities
**Solution**: Configure Trivy to ignore specific vulnerabilities:
```yaml
- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    trivyignores: '.trivyignore'
```

Create `.trivyignore` file:
```
# Ignore specific CVEs
CVE-2021-12345
CVE-2021-67890
```

### 4. Performance Optimization

#### Issue: Slow workflow execution
**Solutions**:
1. Use caching for dependencies
2. Run jobs in parallel where possible
3. Use matrix builds for multiple versions
4. Optimize Docker layer caching

```yaml
strategy:
  matrix:
    python-version: [3.9, 3.10, 3.11]
    
steps:
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ matrix.python-version }}-${{ hashFiles('**/requirements.txt') }}
```

## Monitoring and Notifications

### Workflow Status Badges
Add status badges to your README.md:
```markdown
![CI/CD Pipeline](https://github.com/username/flashcards-project/workflows/CI%2FCD%20Pipeline/badge.svg)
![Code Quality](https://github.com/username/flashcards-project/workflows/Code%20Quality/badge.svg)
```

### Slack Notifications
Add Slack notifications for workflow failures:
```yaml
- name: Slack Notification
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#ci-cd'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications
Configure email notifications in repository settings:
1. Go to repository Settings
2. Click on "Notifications"
3. Configure email preferences for workflow runs

## Best Practices

### 1. Workflow Organization
- Keep workflows focused and single-purpose
- Use reusable workflows for common tasks
- Organize jobs logically with clear dependencies

### 2. Security
- Never commit secrets to the repository
- Use GitHub secrets for sensitive data
- Regularly rotate access tokens
- Use least privilege principle for permissions

### 3. Performance
- Use caching strategically
- Minimize workflow run time
- Use matrix builds for parallel execution
- Optimize Docker builds with multi-stage builds

### 4. Maintenance
- Regularly update action versions
- Monitor workflow performance
- Review and update dependencies
- Keep documentation current

## Troubleshooting Commands

### Local Testing
Test workflows locally using act:
```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflow locally
act -j test
```

### Debug Information
Add debug steps to workflows:
```yaml
- name: Debug Information
  run: |
    echo "Runner OS: ${{ runner.os }}"
    echo "GitHub Event: ${{ github.event_name }}"
    echo "GitHub Ref: ${{ github.ref }}"
    echo "Working Directory: $(pwd)"
    ls -la
```

### Workflow Logs
Access detailed logs:
1. Go to Actions tab in GitHub repository
2. Click on the workflow run
3. Click on the job to see detailed logs
4. Download logs for offline analysis

## Future Enhancements

### Planned Improvements
1. **Deployment automation**: Automated deployment to staging/production
2. **Performance testing**: Automated performance regression testing
3. **Integration testing**: End-to-end testing with real services
4. **Release automation**: Automated release creation and changelog generation

### Advanced Features
1. **Multi-environment deployments**: Support for multiple deployment environments
2. **Blue-green deployments**: Zero-downtime deployment strategy
3. **Canary releases**: Gradual rollout of new versions
4. **Rollback automation**: Automated rollback on deployment failures

This GitHub Actions configuration provides a robust CI/CD pipeline that ensures code quality, security, and reliable deployments for the flashcards application.
