#!/bin/bash

echo "🚀 Starting Flashcards Application - Complete Monitoring Stack"
echo "=============================================================="

# Create monitoring directories if they don't exist
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/dashboards

# Check if main application is running
echo "📊 Checking main application status..."
if ! docker compose ps | grep -q "flashcards-project"; then
    echo "⚠️  Main application not detected. Starting it first..."
    docker compose up -d
    echo "✅ Main application started"
fi

# Rebuild services with monitoring capabilities
echo "🔧 Rebuilding services with monitoring capabilities..."
docker compose build backend-service ocr-service llm-service
echo "✅ Services rebuilt with Prometheus metrics"

# Start monitoring stack
echo "🔍 Starting monitoring services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📋 Monitoring Stack Status:"
echo "=========================="
docker compose -f docker-compose.monitoring.yml ps

echo ""
echo "🎯 Monitoring Stack Access Points:"
echo "=================================="
echo "📊 Grafana Dashboard:    http://localhost:3000"
echo "   Username: admin"
echo "   Password: flashcards2024"
echo "   📈 Available Dashboards:"
echo "      - Flashcards Application - Complete Overview"
echo "      - Backend Service - Detailed Monitoring"
echo "      - OCR Service - Detailed Monitoring"
echo "      - LLM Service - Detailed Monitoring"
echo ""
echo "🔍 Prometheus:           http://localhost:9090"
echo "🚨 AlertManager:         http://localhost:9093"
echo "📈 Node Exporter:        http://localhost:9100"
echo "🐳 cAdvisor:             http://localhost:8080"
echo "📊 Redis Exporter:       http://localhost:9121"
echo "📊 MLflow (if running):  http://localhost:5000"
echo ""
echo "🎯 Application Services:"
echo "======================="
echo "🖥️  Frontend:             http://localhost:8080"
echo "🔧 Backend API:          http://localhost:8002"
echo "🔍 OCR Service:          http://localhost:8000"
echo "🤖 LLM Service:          http://localhost:8001"
echo ""
echo "✅ Monitoring stack is ready!"
echo ""
echo "📚 Quick Start Guide:"
echo "===================="
echo "1. Open Grafana at http://localhost:3000"
echo "2. Login with admin/flashcards2024"
echo "3. Navigate to available dashboards:"
echo "   📊 Complete Overview - All services at a glance"
echo "   🔧 Backend Service - API and business logic metrics"
echo "   🔍 OCR Service - Document processing and ML metrics"
echo "   🤖 LLM Service - AI generation and performance metrics"
echo ""
echo "4. Generate test data to see metrics:"
echo "   # Test OCR service"
echo "   curl -X POST http://localhost:8000/extract -F 'file=@your-image.png'"
echo "   # Test backend API"
echo "   curl http://localhost:8002/health"
echo "   # Test LLM service"
echo "   curl http://localhost:8001/health"
echo ""
echo "5. Monitor alerts in AlertManager: http://localhost:9093"
echo "6. View raw metrics in Prometheus: http://localhost:9090"
echo ""
echo "🔧 Management Commands:"
echo "======================"
echo "Stop monitoring:     docker compose -f docker-compose.monitoring.yml down"
echo "Restart monitoring:  docker compose -f docker-compose.monitoring.yml restart"
echo "View logs:          docker compose -f docker-compose.monitoring.yml logs -f"
