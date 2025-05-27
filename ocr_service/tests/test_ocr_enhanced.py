"""
Comprehensive tests for enhanced OCR service functionality.
"""
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
import io
import json
from unittest.mock import patch, MagicMock

# Use the client from conftest.py instead of creating our own
# This ensures all mocking is properly applied

def create_test_image_with_text(text: str, size=(200, 100)) -> bytes:
    """Create a test image with specified text."""
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)

    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.load_default()
    except:
        font = None

    # Calculate text position (center)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    draw.text((x, y), text, fill='black', font=font)

    # Convert to bytes
    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.getvalue()

def create_test_pdf() -> bytes:
    """Create a simple test PDF with text."""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Test PDF content for OCR")
        pdf_bytes = doc.write()
        doc.close()
        return pdf_bytes
    except ImportError:
        # Return empty bytes if PyMuPDF not available
        return b""

class TestOCREnhanced:
    """Test enhanced OCR functionality."""

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_image_ocr_with_confidence(self, client):
        """Test OCR with confidence scores on image."""
        # Create test image
        test_text = "Hello World"
        image_data = create_test_image_with_text(test_text)

        # Mock OCR functions to avoid dependency on tesseract
        # Determine the correct module path
        try:
            import src.main
            main_module = 'src.main'
        except ImportError:
            main_module = 'ocr_service.src.main'

        with patch(f'{main_module}.extract_text_with_confidence') as mock_ocr:
            mock_ocr.return_value = {
                "text": test_text,
                "filtered_text": test_text,
                "words": ["Hello", "World"],
                "filtered_words": ["Hello", "World"],
                "word_confidences": [95, 90],
                "filtered_confidences": [95, 90],
                "average_confidence": 92.5,
                "filtered_average_confidence": 92.5,
                "word_count": 2,
                "filtered_word_count": 2,
                "low_confidence_words": [],
                "confidence_stats": {
                    "high_confidence_count": 2,
                    "medium_confidence_count": 0,
                    "low_confidence_count": 0,
                    "total_words": 2,
                    "filtering_threshold": 0.0,
                    "words_filtered_out": 0
                }
            }

            response = client.post(
                "/extract",
                files={"file": ("test.png", image_data, "image/png")}
            )

        assert response.status_code == 200
        data = response.json()

        assert data["filename"] == "test.png"
        assert data["file_type"] == "image"
        assert data["text"] == test_text
        assert data["filtered_text"] == test_text
        assert data["average_confidence"] == 92.5
        assert data["filtered_average_confidence"] == 92.5
        assert data["word_count"] == 2
        assert data["filtered_word_count"] == 2
        assert "confidence_stats" in data
        assert data["confidence_stats"]["high_confidence_count"] == 2
        assert data["preprocessing_applied"] is True
        assert data["status"] == "success"

    def test_confidence_filtering(self, client):
        """Test OCR with confidence filtering."""
        # Create test image
        test_text = "Good Bad"
        image_data = create_test_image_with_text(test_text)

        # Mock OCR functions with mixed confidence scores
        try:
            import src.main
            main_module = 'src.main'
        except ImportError:
            main_module = 'ocr_service.src.main'

        with patch(f'{main_module}.extract_text_with_confidence') as mock_ocr:
            mock_ocr.return_value = {
                "text": "Good Bad",
                "filtered_text": "Good",  # Only high confidence word
                "words": ["Good", "Bad"],
                "filtered_words": ["Good"],
                "word_confidences": [95, 30],  # High and low confidence
                "filtered_confidences": [95],
                "average_confidence": 62.5,
                "filtered_average_confidence": 95.0,
                "word_count": 2,
                "filtered_word_count": 1,
                "low_confidence_words": [{"word": "Bad", "confidence": 30}],
                "confidence_stats": {
                    "high_confidence_count": 1,
                    "medium_confidence_count": 0,
                    "low_confidence_count": 1,
                    "total_words": 2,
                    "filtering_threshold": 70.0,
                    "words_filtered_out": 1
                }
            }

            # Test with confidence threshold of 70%
            response = client.post(
                "/extract?min_confidence=70.0",
                files={"file": ("test.png", image_data, "image/png")}
            )

        assert response.status_code == 200
        data = response.json()

        # Check filtering worked correctly
        assert data["text"] == "Good Bad"  # Original text
        assert data["filtered_text"] == "Good"  # Filtered text
        assert data["word_count"] == 2  # Original word count
        assert data["filtered_word_count"] == 1  # Filtered word count
        assert len(data["low_confidence_words"]) == 1
        assert data["low_confidence_words"][0]["word"] == "Bad"
        assert data["confidence_stats"]["words_filtered_out"] == 1
        assert data["confidence_stats"]["filtering_threshold"] == 70.0

    def test_pdf_ocr(self, client):
        """Test PDF OCR functionality."""
        pdf_data = create_test_pdf()

        if pdf_data:  # Only test if PDF creation succeeded
            # Determine the correct module path
            try:
                import src.main
                main_module = 'src.main'
            except ImportError:
                main_module = 'ocr_service.src.main'

            with patch(f'{main_module}.extract_text_from_pdf') as mock_pdf:
                mock_pdf.return_value = {
                    "text": "Test PDF content for OCR",
                    "pages": [{"page": 1, "text": "Test PDF content for OCR"}],
                    "page_count": 1,
                    "total_characters": 25
                }

                response = client.post(
                    "/extract",
                    files={"file": ("test.pdf", pdf_data, "application/pdf")}
                )

            assert response.status_code == 200
            data = response.json()

            assert data["filename"] == "test.pdf"
            assert data["file_type"] == "pdf"
            assert data["page_count"] == 1
            assert data["total_characters"] == 25
            assert data["status"] == "success"

    def test_unsupported_file_type(self, client):
        """Test rejection of unsupported file types."""
        response = client.post(
            "/extract",
            files={"file": ("test.txt", b"some text", "text/plain")}
        )

        assert response.status_code == 415
        assert "Format non supporté" in response.json()["detail"]

    def test_image_preprocessing(self):
        """Test image preprocessing functionality."""
        import sys
        from pathlib import Path

        # Add current directory to Python path for Docker environment
        current_dir = Path(__file__).parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        try:
            from src.main import preprocess_image
        except ImportError:
            try:
                from ocr_service.src.main import preprocess_image
            except ImportError:
                parent_dir = current_dir.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                from ocr_service.src.main import preprocess_image

        # Create a test image
        image = Image.new('RGB', (100, 50), color='white')

        # Test preprocessing
        processed = preprocess_image(image)

        # Should return an image
        assert isinstance(processed, Image.Image)
        # Should be grayscale
        assert processed.mode == 'L'

    def test_confidence_extraction_fallback(self):
        """Test confidence extraction with fallback."""
        import sys
        from pathlib import Path

        # Add current directory to Python path for Docker environment
        current_dir = Path(__file__).parent.parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))

        try:
            from src.main import extract_text_with_confidence
            main_module = 'src.main'
        except ImportError:
            try:
                from ocr_service.src.main import extract_text_with_confidence
                main_module = 'ocr_service.src.main'
            except ImportError:
                parent_dir = current_dir.parent
                if str(parent_dir) not in sys.path:
                    sys.path.insert(0, str(parent_dir))
                from ocr_service.src.main import extract_text_with_confidence
                main_module = 'ocr_service.src.main'

        # Create a test image
        image = Image.new('RGB', (100, 50), color='white')

        # Mock pytesseract to raise an exception for confidence, but work for basic OCR
        with patch(f'{main_module}.pytesseract.image_to_data') as mock_data, \
             patch(f'{main_module}.pytesseract.image_to_string') as mock_string:

            mock_data.side_effect = Exception("OCR failed")
            mock_string.return_value = "fallback text"

            result = extract_text_with_confidence(image)

            assert result["text"] == "fallback text"
            assert result["filtered_text"] == "fallback text"
            assert result["average_confidence"] == 0
            assert result["filtered_average_confidence"] == 0
            assert result["word_count"] == 2  # "fallback text" = 2 words
            assert result["filtered_word_count"] == 2

    def test_rate_limiting(self, client):
        """Test that basic requests work (rate limiting tested separately)."""
        # Create test image
        image_data = create_test_image_with_text("Test")

        # Mock OCR to avoid actual processing
        # Determine the correct module path
        try:
            import src.main
            main_module = 'src.main'
        except ImportError:
            main_module = 'ocr_service.src.main'

        with patch(f'{main_module}.extract_text_with_confidence') as mock_ocr:
            mock_ocr.return_value = {
                "text": "Test",
                "filtered_text": "Test",
                "words": ["Test"],
                "filtered_words": ["Test"],
                "word_confidences": [95],
                "filtered_confidences": [95],
                "average_confidence": 95.0,
                "filtered_average_confidence": 95.0,
                "word_count": 1,
                "filtered_word_count": 1,
                "low_confidence_words": [],
                "confidence_stats": {
                    "high_confidence_count": 1,
                    "medium_confidence_count": 0,
                    "low_confidence_count": 0,
                    "total_words": 1,
                    "filtering_threshold": 0.0,
                    "words_filtered_out": 0
                }
            }

            # Make a few requests to test basic functionality
            response = client.post(
                "/extract",
                files={"file": ("test.png", image_data, "image/png")}
            )

        # Should work for basic requests
        assert response.status_code == 200
        assert response.json()["text"] == "Test"

    def test_pdf_not_supported(self, client):
        """Test PDF handling when PyMuPDF is not available."""
        # Determine the correct module path
        try:
            import src.main
            main_module = 'src.main'
        except ImportError:
            main_module = 'ocr_service.src.main'

        with patch(f'{main_module}.PDF_SUPPORT', False):
            response = client.post(
                "/extract",
                files={"file": ("test.pdf", b"fake pdf", "application/pdf")}
            )

        assert response.status_code == 501
        assert "PDF support not available" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
