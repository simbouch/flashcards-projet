"""
Comprehensive tests for enhanced OCR service functionality.
"""
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw, ImageFont
import io
import json
from unittest.mock import patch, MagicMock

# Import the app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.main import app

client = TestClient(app)

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
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_image_ocr_with_confidence(self):
        """Test OCR with confidence scores on image."""
        # Create test image
        test_text = "Hello World"
        image_data = create_test_image_with_text(test_text)
        
        # Mock OCR functions to avoid dependency on tesseract
        with patch('src.main.extract_text_with_confidence') as mock_ocr:
            mock_ocr.return_value = {
                "text": test_text,
                "words": ["Hello", "World"],
                "word_confidences": [95, 90],
                "average_confidence": 92.5,
                "word_count": 2
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
        assert data["average_confidence"] == 92.5
        assert data["word_count"] == 2
        assert data["preprocessing_applied"] is True
        assert data["status"] == "success"
    
    def test_pdf_ocr(self):
        """Test PDF OCR functionality."""
        pdf_data = create_test_pdf()
        
        if pdf_data:  # Only test if PDF creation succeeded
            with patch('src.main.extract_text_from_pdf') as mock_pdf:
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
    
    def test_unsupported_file_type(self):
        """Test rejection of unsupported file types."""
        response = client.post(
            "/extract",
            files={"file": ("test.txt", b"some text", "text/plain")}
        )
        
        assert response.status_code == 415
        assert "Format non supporté" in response.json()["detail"]
    
    def test_image_preprocessing(self):
        """Test image preprocessing functionality."""
        from src.main import preprocess_image
        
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
        from src.main import extract_text_with_confidence
        
        # Create a test image
        image = Image.new('RGB', (100, 50), color='white')
        
        # Mock pytesseract to raise an exception for confidence, but work for basic OCR
        with patch('src.main.pytesseract.image_to_data') as mock_data, \
             patch('src.main.pytesseract.image_to_string') as mock_string:
            
            mock_data.side_effect = Exception("OCR failed")
            mock_string.return_value = "fallback text"
            
            result = extract_text_with_confidence(image)
            
            assert result["text"] == "fallback text"
            assert result["average_confidence"] == 0
            assert result["word_count"] == 2  # "fallback text" = 2 words
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Create test image
        image_data = create_test_image_with_text("Test")
        
        # Mock OCR to avoid actual processing
        with patch('src.main.extract_text_with_confidence') as mock_ocr:
            mock_ocr.return_value = {
                "text": "Test",
                "words": ["Test"],
                "word_confidences": [95],
                "average_confidence": 95.0,
                "word_count": 1
            }
            
            # Make multiple requests quickly
            responses = []
            for i in range(12):  # Exceed the 10/minute limit
                response = client.post(
                    "/extract",
                    files={"file": (f"test{i}.png", image_data, "image/png")}
                )
                responses.append(response)
        
        # Some requests should be rate limited
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0
    
    @patch('src.main.PDF_SUPPORT', False)
    def test_pdf_not_supported(self):
        """Test PDF handling when PyMuPDF is not available."""
        response = client.post(
            "/extract",
            files={"file": ("test.pdf", b"fake pdf", "application/pdf")}
        )
        
        assert response.status_code == 501
        assert "PDF support not available" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
