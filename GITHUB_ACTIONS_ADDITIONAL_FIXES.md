# GitHub Actions Additional Fixes and Advanced Configuration

This document provides additional fixes, advanced configurations, and troubleshooting solutions for GitHub Actions workflows in the flashcards project.

## Advanced Workflow Configurations

### 1. Multi-Environment Deployment Workflow

```yaml
name: Multi-Environment Deployment

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
      force_deploy:
        description: 'Force deployment even if tests fail'
        required: false
        default: false
        type: boolean

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/main' || github.event.inputs.environment == 'staging'
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment commands here
    
    - name: Run Smoke Tests
      run: |
        echo "Running smoke tests on staging"
        # Add smoke test commands here
    
    - name: Notify Slack
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        channel: '#deployments'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  deploy-production:
    if: github.event.inputs.environment == 'production'
    needs: [deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Deploy to Production
      run: |
        echo "Deploying to production environment"
        # Add production deployment commands here
    
    - name: Run Health Checks
      run: |
        echo "Running health checks on production"
        # Add health check commands here
```

### 2. Performance Testing Workflow

```yaml
name: Performance Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM
  workflow_dispatch:

jobs:
  performance-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Compose
      run: |
        docker-compose up -d
        sleep 30  # Wait for services to start
    
    - name: Install k6
      run: |
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6
    
    - name: Run Performance Tests
      run: |
        k6 run --out json=results.json performance-tests/load-test.js
    
    - name: Upload Results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: results.json
    
    - name: Analyze Results
      run: |
        python scripts/analyze-performance.py results.json
    
    - name: Comment PR with Results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const results = JSON.parse(fs.readFileSync('performance-summary.json'));
          
          const comment = `## Performance Test Results
          
          - **Average Response Time**: ${results.avg_response_time}ms
          - **95th Percentile**: ${results.p95_response_time}ms
          - **Requests per Second**: ${results.rps}
          - **Error Rate**: ${results.error_rate}%
          
          ${results.status === 'pass' ? '✅ Performance tests passed' : '❌ Performance regression detected'}
          `;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
```

### 3. Security Scanning and Compliance

```yaml
name: Security and Compliance

on:
  push:
    branches: [ main, dev ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Run Bandit Security Scan
      run: |
        pip install bandit
        bandit -r backend_service/src ocr_service/src llm_service/src -f json -o bandit-report.json
    
    - name: Run Safety Check
      run: |
        pip install safety
        safety check --json --output safety-report.json
    
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/secrets
          p/owasp-top-ten
    
    - name: Docker Security Scan
      run: |
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
          -v $PWD:/root/.cache/ aquasec/trivy:latest \
          image --format json --output docker-security.json \
          flashcards-backend:latest
    
    - name: Upload Security Reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
          docker-security.json

  compliance-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: License Compliance Check
      run: |
        pip install pip-licenses
        pip-licenses --format=json --output-file=licenses.json
    
    - name: GDPR Compliance Check
      run: |
        # Custom script to check for GDPR compliance
        python scripts/gdpr-check.py
    
    - name: Generate Compliance Report
      run: |
        python scripts/generate-compliance-report.py
```

## Advanced Troubleshooting

### 1. Debugging Failed Workflows

#### Enable Debug Logging
Add these secrets to your repository:
- `ACTIONS_STEP_DEBUG`: `true`
- `ACTIONS_RUNNER_DEBUG`: `true`

#### Debug Action
```yaml
- name: Debug Environment
  run: |
    echo "=== Environment Variables ==="
    env | sort
    echo "=== System Information ==="
    uname -a
    echo "=== Disk Space ==="
    df -h
    echo "=== Memory ==="
    free -h
    echo "=== Docker Info ==="
    docker info
    echo "=== Docker Images ==="
    docker images
    echo "=== Docker Containers ==="
    docker ps -a
```

### 2. Handling Flaky Tests

#### Retry Failed Tests
```yaml
- name: Run Tests with Retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: python -m pytest tests/ -v
```

#### Test Sharding
```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
    
steps:
- name: Run Test Shard
  run: |
    python -m pytest tests/ -v --shard-id=${{ matrix.shard }} --num-shards=4
```

### 3. Resource Optimization

#### Conditional Job Execution
```yaml
jobs:
  check-changes:
    runs-on: ubuntu-latest
    outputs:
      backend-changed: ${{ steps.changes.outputs.backend }}
      frontend-changed: ${{ steps.changes.outputs.frontend }}
      ocr-changed: ${{ steps.changes.outputs.ocr }}
      llm-changed: ${{ steps.changes.outputs.llm }}
    steps:
    - uses: actions/checkout@v4
    - uses: dorny/paths-filter@v2
      id: changes
      with:
        filters: |
          backend:
            - 'backend_service/**'
          frontend:
            - 'frontend/**'
          ocr:
            - 'ocr_service/**'
          llm:
            - 'llm_service/**'

  test-backend:
    needs: check-changes
    if: needs.check-changes.outputs.backend-changed == 'true'
    runs-on: ubuntu-latest
    steps:
    - name: Test Backend
      run: echo "Testing backend changes"
```

#### Parallel Matrix Builds
```yaml
strategy:
  matrix:
    service: [backend, ocr, llm, frontend]
    python-version: [3.9, 3.10, 3.11]
  fail-fast: false
  
steps:
- name: Test ${{ matrix.service }} with Python ${{ matrix.python-version }}
  run: |
    cd ${{ matrix.service }}_service
    python${{ matrix.python-version }} -m pytest
```

## Custom Actions

### 1. Reusable Workflow for Service Testing

Create `.github/workflows/test-service.yml`:
```yaml
name: Test Service

on:
  workflow_call:
    inputs:
      service-name:
        required: true
        type: string
      python-version:
        required: false
        type: string
        default: '3.10'

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ inputs.python-version }}
    
    - name: Install dependencies
      run: |
        cd ${{ inputs.service-name }}_service
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        cd ${{ inputs.service-name }}_service
        python -m pytest tests/ -v --cov=src
```

Use in main workflow:
```yaml
jobs:
  test-backend:
    uses: ./.github/workflows/test-service.yml
    with:
      service-name: backend
      python-version: '3.10'
  
  test-ocr:
    uses: ./.github/workflows/test-service.yml
    with:
      service-name: ocr
      python-version: '3.10'
```

### 2. Custom Action for MLflow Tracking

Create `.github/actions/mlflow-track/action.yml`:
```yaml
name: 'MLflow Tracking'
description: 'Track workflow metrics in MLflow'
inputs:
  mlflow-uri:
    description: 'MLflow tracking URI'
    required: true
  experiment-name:
    description: 'MLflow experiment name'
    required: true
  run-name:
    description: 'MLflow run name'
    required: false
    default: 'github-actions-run'

runs:
  using: 'composite'
  steps:
  - name: Install MLflow
    shell: bash
    run: pip install mlflow
  
  - name: Track Workflow
    shell: bash
    run: |
      python -c "
      import mlflow
      import os
      
      mlflow.set_tracking_uri('${{ inputs.mlflow-uri }}')
      mlflow.set_experiment('${{ inputs.experiment-name }}')
      
      with mlflow.start_run(run_name='${{ inputs.run-name }}'):
          mlflow.log_param('github_ref', os.environ.get('GITHUB_REF'))
          mlflow.log_param('github_sha', os.environ.get('GITHUB_SHA'))
          mlflow.log_param('github_actor', os.environ.get('GITHUB_ACTOR'))
          mlflow.log_param('workflow_name', os.environ.get('GITHUB_WORKFLOW'))
      "
```

## Monitoring and Alerting

### 1. Workflow Monitoring Dashboard

Create a monitoring script that tracks workflow metrics:
```python
# scripts/monitor-workflows.py
import requests
import json
from datetime import datetime, timedelta

def get_workflow_runs(repo, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    url = f'https://api.github.com/repos/{repo}/actions/runs'
    response = requests.get(url, headers=headers)
    
    return response.json()

def analyze_workflow_performance(runs):
    success_rate = sum(1 for run in runs if run['conclusion'] == 'success') / len(runs)
    avg_duration = sum(run['run_duration_ms'] for run in runs) / len(runs)
    
    return {
        'success_rate': success_rate,
        'avg_duration_minutes': avg_duration / 60000,
        'total_runs': len(runs)
    }

# Usage in workflow
if __name__ == '__main__':
    repo = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GITHUB_TOKEN']
    
    runs = get_workflow_runs(repo, token)
    metrics = analyze_workflow_performance(runs['workflow_runs'][:50])
    
    print(f"Workflow Performance Metrics: {json.dumps(metrics, indent=2)}")
```

### 2. Slack Integration for Workflow Status

```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#ci-cd-alerts'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
    fields: repo,message,commit,author,action,eventName,ref,workflow
    custom_payload: |
      {
        "attachments": [{
          "color": "danger",
          "title": "Workflow Failed",
          "text": "Workflow ${{ github.workflow }} failed in ${{ github.repository }}",
          "fields": [
            {
              "title": "Branch",
              "value": "${{ github.ref }}",
              "short": true
            },
            {
              "title": "Commit",
              "value": "${{ github.sha }}",
              "short": true
            },
            {
              "title": "Author",
              "value": "${{ github.actor }}",
              "short": true
            }
          ],
          "actions": [
            {
              "type": "button",
              "text": "View Workflow",
              "url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
          ]
        }]
      }
```

## Best Practices for Large Projects

### 1. Workflow Organization
- Use workflow templates for consistency
- Implement reusable workflows for common tasks
- Organize workflows by purpose (CI, CD, security, etc.)
- Use clear naming conventions

### 2. Performance Optimization
- Use caching strategically
- Implement conditional execution
- Use matrix builds for parallel execution
- Optimize Docker builds with layer caching

### 3. Security Best Practices
- Use OIDC for cloud authentication
- Implement least privilege access
- Regularly rotate secrets
- Use dependency scanning

### 4. Maintenance
- Regularly update action versions
- Monitor workflow performance
- Implement automated dependency updates
- Keep documentation current

## Common Issues and Solutions

### Issue: Workflow runs out of disk space
**Solution**: Clean up unnecessary files and use smaller base images
```yaml
- name: Free Disk Space
  run: |
    sudo rm -rf /usr/share/dotnet
    sudo rm -rf /opt/ghc
    sudo rm -rf "/usr/local/share/boost"
    sudo rm -rf "$AGENT_TOOLSDIRECTORY"
    df -h
```

### Issue: Docker build timeouts
**Solution**: Optimize Dockerfile and use multi-stage builds
```dockerfile
# Use multi-stage builds
FROM python:3.10-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . .
```

### Issue: Flaky network tests
**Solution**: Implement retry logic and use test containers
```yaml
- name: Start Test Services
  run: |
    docker-compose -f docker-compose.test.yml up -d
    ./scripts/wait-for-services.sh
```

This comprehensive guide provides advanced configurations and troubleshooting solutions for GitHub Actions workflows, ensuring robust and reliable CI/CD pipelines for the flashcards application.
