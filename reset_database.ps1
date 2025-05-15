# Reset the database to only have native decks
# This script will:
# 1. Delete all user-created decks
# 2. Delete all user-created documents
# 3. Ensure the native decks are recreated

Write-Host "Resetting database to only have native decks..." -ForegroundColor Green

# Stop the containers
Write-Host "Stopping containers..." -ForegroundColor Yellow
docker-compose down

# Remove the database volume to completely reset the database
Write-Host "Removing database volume..." -ForegroundColor Yellow
docker volume rm flashcards-project_postgres-data

# Start the containers again
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose up -d

# Wait for the backend service to be ready
Write-Host "Waiting for backend service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Database reset complete!" -ForegroundColor Green
Write-Host "The application now only has the native decks." -ForegroundColor Green
Write-Host "You can now log in and create new decks and documents." -ForegroundColor Green
