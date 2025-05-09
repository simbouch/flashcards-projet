"""
OCR service client.
"""
import httpx
import aiofiles
from pathlib import Path
from typing import Dict, Any, Optional
from ..config import settings
from ..logger_config import logger

class OCRServiceClient:
    """Client for the OCR service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the OCR service client.
        
        Args:
            base_url: Base URL of the OCR service.
        """
        self.base_url = base_url or settings.OCR_SERVICE_URL
        logger.debug(f"Initialized OCR service client with base URL: {self.base_url}")
    
    async def extract_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from an image using the OCR service.
        
        Args:
            file_path: Path to the image file.
            
        Returns:
            Dictionary with extracted text.
            
        Raises:
            Exception: If OCR service request fails.
        """
        logger.info(f"Extracting text from file: {file_path}")
        
        # Read file content
        async with aiofiles.open(file_path, "rb") as f:
            file_content = await f.read()
        
        # Prepare file for upload
        files = {"file": (file_path.name, file_content, f"image/{file_path.suffix[1:]}")}
        
        # Send request to OCR service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/extract",
                    files=files,
                    timeout=30.0  # 30 seconds timeout
                )
                
                # Check response status
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                logger.info(f"Successfully extracted {len(result.get('text', ''))} characters of text")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"OCR service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"OCR service error: {e.response.status_code} - {e.response.text}")
            
        except httpx.RequestError as e:
            logger.error(f"OCR service request error: {str(e)}")
            raise Exception(f"OCR service request error: {str(e)}")
            
        except Exception as e:
            logger.exception(f"Unexpected error during OCR text extraction: {str(e)}")
            raise
