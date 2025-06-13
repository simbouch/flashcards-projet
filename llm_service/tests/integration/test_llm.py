import requests
import json
import os
import pytest


@pytest.mark.integration
def test_llm_health():
    """Test if the LLM service is running."""
    # Skip this test in CI environment where services aren't running
    if os.getenv('TESTING') == 'true' or os.getenv('CI') == 'true':
        pytest.skip("Skipping integration test in CI environment")

    url = "http://localhost:8001/health"

    try:
        response = requests.get(url, timeout=5)
        assert response.status_code == 200, f"LLM service health check failed: {response.status_code}"

        # Verify response content
        health_data = response.json()
        assert "status" in health_data, "Health response missing status field"
        assert health_data["status"] == "healthy", f"Service not healthy: {health_data}"

    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"LLM service not available: {e}")
    except requests.exceptions.Timeout as e:
        pytest.fail(f"LLM service timeout: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error connecting to LLM service: {e}")


@pytest.mark.integration
def test_generate_flashcards():
    """Test flashcard generation from text using the LLM service."""
    # Skip this test in CI environment where services aren't running
    if os.getenv('TESTING') == 'true' or os.getenv('CI') == 'true':
        pytest.skip("Skipping integration test in CI environment")

    url = "http://localhost:8001/generate"
    test_text = "The French Revolution was a period of radical political and social change in France."

    data = {
        "text": test_text,
        "task": "flashcards"
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        assert response.status_code == 200, f"Flashcard generation failed: {response.status_code}"

        result = response.json()
        assert "flashcards" in result, "Response missing flashcards field"

        flashcards = result["flashcards"]
        assert isinstance(flashcards, list), "Flashcards should be a list"
        assert len(flashcards) > 0, "Should generate at least one flashcard"

        # Verify flashcard structure
        for flashcard in flashcards:
            assert "question" in flashcard, "Flashcard missing question field"
            assert "answer" in flashcard, "Flashcard missing answer field"
            assert len(flashcard["question"].strip()) > 0, "Question should not be empty"
            assert len(flashcard["answer"].strip()) > 0, "Answer should not be empty"

    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"LLM service not available: {e}")
    except requests.exceptions.Timeout as e:
        pytest.fail(f"LLM service timeout: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in flashcard generation: {e}")


def check_llm_health():
    """Helper function to check LLM service health - for manual testing."""
    url = "http://localhost:8001/health"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"LLM service health check failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Error connecting to LLM service: {e}")
        return False

def generate_flashcards(text):
    """Generate flashcards from text using the LLM service."""
    url = "http://localhost:8001/generate"

    data = {
        "text": text,
        "task": "flashcards"
    }

    print(f"Sending request to {url} with data: {json.dumps(data, indent=2)}")

    try:
        response = requests.post(url, json=data)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response JSON: {json.dumps(result, indent=2)}")
            return result.get("flashcards", [])
        else:
            print(f"Flashcard generation failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error connecting to LLM service: {e}")
        return None

def main():
    """Main function for manual testing."""
    # Check if the LLM service is running
    print("Checking LLM service health...")
    if not check_llm_health():
        print("LLM service is not running or not responding correctly.")
        return
    print("LLM service is running.")

    # Use an extremely simple text
    text = """The French Revolution was a period of radical political and social change in France that began with the Estates General of 1789 and ended with the formation of the French Consulate in November 1799. Many of its ideas are considered fundamental principles of liberal democracy, while phrases like Liberté, égalité, fraternité reappeared in other revolts, such as the 1917 Russian Revolution, and inspired campaigns for the abolition of slavery and universal suffrage. The Revolution resulted in the suppression of the feudal system, emancipation of the individual, a greater division of landed property, abolition of the privileges of noble birth, and nominal establishment of equality among men. The French Revolution differed from other revolutions in being not only national, for it intended to benefit all humanity."""

    # Generate flashcards
    print("\nGenerating flashcards from text...")
    flashcards = generate_flashcards(text)

    if not flashcards:
        print("Failed to generate flashcards.")
        return

    # Display the flashcards
    print("\nGenerated Flashcards:")
    for i, flashcard in enumerate(flashcards, 1):
        print(f"\nFlashcard {i}:")
        print(f"Question: {flashcard.get('question')}")
        print(f"Answer: {flashcard.get('answer')}")

    print("\nTest completed successfully!")

if __name__ == "__main__":
    main()
