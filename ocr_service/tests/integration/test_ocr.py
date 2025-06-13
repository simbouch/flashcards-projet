import requests
import json
import sys
import os
import pytest
from pathlib import Path


@pytest.mark.integration
def test_ocr_health():
    """Test if the OCR service is running."""
    # Skip this test in CI environment where services aren't running
    if os.getenv('TESTING') == 'true' or os.getenv('CI') == 'true':
        pytest.skip("Skipping integration test in CI environment")

    url = "http://localhost:8000/health"

    try:
        response = requests.get(url, timeout=5)
        assert response.status_code == 200, f"OCR service health check failed: {response.status_code}"

        # Verify response content
        health_data = response.json()
        assert "status" in health_data, "Health response missing status field"
        assert health_data["status"] == "healthy", f"Service not healthy: {health_data}"

    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"OCR service not available: {e}")
    except requests.exceptions.Timeout as e:
        pytest.fail(f"OCR service timeout: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error connecting to OCR service: {e}")


@pytest.mark.integration
def test_extract_text_from_image():
    """Test text extraction from image using the OCR service."""
    # Skip this test in CI environment where services aren't running
    if os.getenv('TESTING') == 'true' or os.getenv('CI') == 'true':
        pytest.skip("Skipping integration test in CI environment")

    # Use test image from fixtures
    test_image_path = Path(__file__).parent.parent / "fixtures" / "test.png"
    if not test_image_path.exists():
        pytest.skip(f"Test image not found: {test_image_path}")

    url = "http://localhost:8000/extract"

    try:
        with open(test_image_path, "rb") as f:
            files = {"file": ("test.png", f, "image/png")}
            response = requests.post(url, files=files, timeout=30)

        assert response.status_code == 200, f"OCR extraction failed: {response.status_code}"

        result = response.json()
        assert "text" in result, "Response missing text field"
        assert "confidence" in result, "Response missing confidence field"

        extracted_text = result["text"]
        assert isinstance(extracted_text, str), "Extracted text should be a string"
        # Note: We don't assert text length > 0 because the test image might be empty

        confidence = result["confidence"]
        assert isinstance(confidence, (int, float)), "Confidence should be a number"
        assert 0 <= confidence <= 100, "Confidence should be between 0 and 100"

    except requests.exceptions.ConnectionError as e:
        pytest.skip(f"OCR service not available: {e}")
    except requests.exceptions.Timeout as e:
        pytest.fail(f"OCR service timeout: {e}")
    except Exception as e:
        pytest.fail(f"Unexpected error in OCR extraction: {e}")


def extract_text_from_image(image_path):
    """Helper function for manual testing - Extract text from an image using the OCR service."""
    url = "http://localhost:8000/extract"

    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        # Create a multipart form with the image file
        files = {"file": (image_path, f, "image/png")}

        # Make the request
        response = requests.post(url, files=files, timeout=30)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            return result.get("text", "")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def main():
    """Main function for manual testing."""
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <image_path>")
        return

    image_path = sys.argv[1]
    text = extract_text_from_image(image_path)

    if text:
        print("Extracted Text:")
        print(text)
    else:
        print("Failed to extract text from the image.")

if __name__ == "__main__":
    main()
