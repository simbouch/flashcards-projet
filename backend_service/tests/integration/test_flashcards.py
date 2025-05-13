import requests
import json
import sys

def login(username, password):
    """Login to the backend service and get an access token."""
    url = "http://localhost:8002/api/v1/auth/login"
    data = {
        "username": username,
        "password": password
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def extract_text_from_image(image_path):
    """Extract text from an image using the OCR service."""
    url = "http://localhost:8000/extract"

    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/png")}
        response = requests.post(url, files=files)

        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            print(f"OCR failed: {response.status_code}")
            print(response.text)
            return None

def create_document(token, title, image_path):
    """Create a new document in the backend service by uploading an image."""
    url = "http://localhost:8002/api/v1/documents/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        # Create a multipart form with the image file
        files = {
            "file": (image_path, f, "image/png")
        }
        data = {
            "title": title
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Document creation failed: {response.status_code}")
            print(response.text)
            return None

def get_decks(token):
    """Get all decks for the current user."""
    url = "http://localhost:8002/api/v1/decks/"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get decks failed: {response.status_code}")
        print(response.text)
        return None

def get_deck_for_document(token, document_id):
    """Get the deck associated with a document."""
    decks = get_decks(token)
    if not decks:
        return None

    for deck in decks:
        if deck.get("document_id") == document_id:
            return deck

    return None

def get_flashcards(token, deck_id):
    """Get flashcards for a deck."""
    url = f"http://localhost:8002/api/v1/flashcards/?deck_id={deck_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Get flashcards failed: {response.status_code}")
        print(response.text)
        return None

def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python test_flashcards.py <image_path> <username> <password>")
        return

    image_path = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    # Login
    print("Logging in...")
    token = login(username, password)
    if not token:
        return
    print("Login successful!")

    # Extract text from image
    print("\nExtracting text from image...")
    text = extract_text_from_image(image_path)
    if not text:
        return
    print("Text extraction successful!")
    print(f"Extracted text: {text[:100]}...")

    # Create document by uploading the image directly
    print("\nCreating document...")
    document_id = create_document(token, "Test Document", image_path)
    if not document_id:
        return
    print(f"Document created with ID: {document_id}")

    # Wait for flashcards to be generated
    print("\nWaiting for flashcards to be generated...")
    import time

    # Wait up to 30 seconds for flashcards to be generated
    max_attempts = 6
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(5)  # Wait 5 seconds between attempts

        # Check if the document status is complete
        url = f"http://localhost:8002/api/v1/documents/{document_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            status = response.json().get("status")
            print(f"Document status: {status}")
            if status == "flashcard_complete":
                break
        else:
            print(f"Failed to check document status: {response.status_code}")
            print(response.text)

    # Get the deck for the document
    print("\nGetting deck for the document...")
    deck = get_deck_for_document(token, document_id)
    if not deck:
        print("No deck found for the document.")
        return
    print(f"Found deck: {deck.get('title')} (ID: {deck.get('id')})")

    # Get flashcards
    print("\nGetting flashcards...")
    flashcards = get_flashcards(token, deck.get('id'))
    if not flashcards:
        print("No flashcards found for the deck.")
        return

    print(f"Found {len(flashcards)} flashcards:")
    for i, flashcard in enumerate(flashcards, 1):
        print(f"\nFlashcard {i}:")
        print(f"Question: {flashcard.get('question')}")
        print(f"Answer: {flashcard.get('answer')}")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
