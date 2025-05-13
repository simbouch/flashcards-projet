# PowerShell script to reset the database and create fresh test decks
# This script will:
# 1. Stop all containers
# 2. Remove all containers and volumes
# 3. Start the services again
# 4. Create new test decks

Write-Output "Step 1: Stopping all containers..."
docker-compose down -v

Write-Output "Step 2: Starting all services..."
docker-compose up -d

# Wait for services to be ready
Write-Output "Waiting for services to be ready..."
Start-Sleep -Seconds 15

# Sample flashcards for different subjects
$sampleDecks = @{
    "Programming Concepts" = @(
        @{
            question = "What is a variable?"
            answer = "A named storage location in memory that holds a value."
        },
        @{
            question = "What is object-oriented programming?"
            answer = "A programming paradigm based on the concept of 'objects', which can contain data and code."
        },
        @{
            question = "What is a function?"
            answer = "A reusable block of code that performs a specific task."
        },
        @{
            question = "What is inheritance in OOP?"
            answer = "A mechanism where a class can inherit properties and methods from another class."
        },
        @{
            question = "What is a data structure?"
            answer = "A specialized format for organizing, processing, retrieving and storing data."
        }
    )
    "World Capitals" = @(
        @{
            question = "What is the capital of France?"
            answer = "Paris"
        },
        @{
            question = "What is the capital of Japan?"
            answer = "Tokyo"
        },
        @{
            question = "What is the capital of Brazil?"
            answer = "Brasília"
        },
        @{
            question = "What is the capital of Australia?"
            answer = "Canberra"
        },
        @{
            question = "What is the capital of Egypt?"
            answer = "Cairo"
        }
    )
    "Science Facts" = @(
        @{
            question = "What is photosynthesis?"
            answer = "The process by which green plants and some other organisms use sunlight to synthesize foods with carbon dioxide and water."
        },
        @{
            question = "What is the chemical symbol for gold?"
            answer = "Au (from the Latin 'aurum')"
        },
        @{
            question = "What is Newton's First Law of Motion?"
            answer = "An object at rest stays at rest, and an object in motion stays in motion unless acted upon by an external force."
        },
        @{
            question = "What is the speed of light in a vacuum?"
            answer = "299,792,458 meters per second"
        },
        @{
            question = "What is the smallest unit of life?"
            answer = "The cell"
        }
    )
}

Write-Output "Step 3: Registering test user..."
$registerData = @{
    username = "testuser"
    email = "test@example.com"
    password = "Password123"
    full_name = "Test User"
}

try {
    Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/register" -Method POST -Body ($registerData | ConvertTo-Json) -ContentType "application/json"
    Write-Output "User registered successfully."
} catch {
    Write-Output "User may already exist, trying to login..."
}

Write-Output "Step 4: Logging in as testuser..."
$loginData = @{
    username = "testuser"
    password = "Password123"
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/x-www-form-urlencoded"
    $token = ($response.Content | ConvertFrom-Json).access_token
    Write-Output "Successfully logged in and got access token"
} catch {
    Write-Output "Failed to login: $_"
    exit 1
}

# Set up headers with the token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Output "Step 5: Creating test decks with flashcards..."
foreach ($deckTitle in $sampleDecks.Keys) {
    Write-Output "Creating deck: $deckTitle"
    
    # Create the deck - make all decks public
    $deckData = @{
        title = $deckTitle
        description = "A sample deck about $deckTitle"
        is_public = $true
    }
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/decks/" -Method POST -Body ($deckData | ConvertTo-Json) -Headers $headers
        $deck = $response.Content | ConvertFrom-Json
        Write-Output "Deck created successfully with ID: $($deck.id)"
        
        # Add flashcards to the deck
        foreach ($card in $sampleDecks[$deckTitle]) {
            $cardData = @{
                question = $card.question
                answer = $card.answer
                deck_id = $deck.id
            }
            
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/flashcards/" -Method POST -Body ($cardData | ConvertTo-Json) -Headers $headers
                $flashcard = $response.Content | ConvertFrom-Json
                Write-Output "Created flashcard: $($flashcard.id)"
            }
            catch {
                Write-Output "Failed to create flashcard: $_"
            }
        }
        
        Write-Output "Added $($sampleDecks[$deckTitle].Count) flashcards to deck: $deckTitle"
    }
    catch {
        Write-Output "Failed to create deck: $_"
    }
}

Write-Output "Step 6: Restarting the frontend service..."
docker-compose restart frontend-service

Write-Output "Setup complete! You can now access the flashcards at http://localhost:8080"
Write-Output "Login with username: testuser and password: Password123"
