# PowerShell script to create test decks with flashcards
# This script uses the API directly instead of accessing the database

# Login credentials
$loginData = @{
    username = "testuser"
    password = "Password123"
}

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

# Step 1: Login to get access token
Write-Output "Logging in as testuser..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/x-www-form-urlencoded"
    $token = ($response.Content | ConvertFrom-Json).access_token
    Write-Output "Successfully logged in and got access token"
}
catch {
    # If login fails, try to register the user first
    Write-Output "Login failed. Attempting to register user..."
    $registerData = @{
        username = "testuser"
        email = "test@example.com"
        password = "Password123"
        full_name = "Test User"
    }

    try {
        Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/register" -Method POST -Body ($registerData | ConvertTo-Json) -ContentType "application/json"
        Write-Output "User registered successfully. Trying to login again..."

        $response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/auth/login" -Method POST -Body $loginData -ContentType "application/x-www-form-urlencoded"
        $token = ($response.Content | ConvertFrom-Json).access_token
        Write-Output "Successfully logged in and got access token"
    }
    catch {
        Write-Output "Failed to register user: $_"
        exit 1
    }
}

# Set up headers with the token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get existing decks and delete them
Write-Output "Getting existing decks..."
$response = Invoke-WebRequest -Uri "http://localhost:8002/api/v1/decks/" -Method GET -Headers $headers
$existingDecks = $response.Content | ConvertFrom-Json

foreach ($deck in $existingDecks) {
    Write-Output "Deleting deck: $($deck.title) (ID: $($deck.id))"
    try {
        Invoke-WebRequest -Uri "http://localhost:8002/api/v1/decks/$($deck.id)" -Method DELETE -Headers $headers
        Write-Output "Deck deleted successfully"
    }
    catch {
        Write-Output "Failed to delete deck: $_"
    }
}

# Step 3: Create new decks with flashcards
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

Write-Output "Test data creation complete!"
Write-Output "You can now access the flashcards at http://localhost:8001"
