"""
LLM service client.
"""
import httpx
from typing import Dict, Any, List, Optional
from ..config import settings
from ..logger_config import logger

class LLMServiceClient:
    """Client for the LLM service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the LLM service client.
        
        Args:
            base_url: Base URL of the LLM service.
        """
        self.base_url = base_url or settings.LLM_SERVICE_URL
        logger.debug(f"Initialized LLM service client with base URL: {self.base_url}")
    
    async def generate_flashcards(self, text: str, num_cards: int = 5) -> Dict[str, Any]:
        """
        Generate flashcards from text using the LLM service.
        
        Args:
            text: Text to generate flashcards from.
            num_cards: Number of flashcards to generate.
            
        Returns:
            Dictionary with generated flashcards.
            
        Raises:
            Exception: If LLM service request fails.
        """
        logger.info(f"Generating {num_cards} flashcards from {len(text)} characters of text")
        
        # Prepare request data
        data = {
            "text": text,
            "num_cards": num_cards
        }
        
        # Send request to LLM service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate",
                    json=data,
                    timeout=60.0  # 60 seconds timeout
                )
                
                # Check response status
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                logger.info(f"Successfully generated {len(result.get('flashcards', []))} flashcards")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM service error: {e.response.status_code} - {e.response.text}")
            
        except httpx.RequestError as e:
            logger.error(f"LLM service request error: {str(e)}")
            raise Exception(f"LLM service request error: {str(e)}")
            
        except Exception as e:
            logger.exception(f"Unexpected error during flashcard generation: {str(e)}")
            raise
    
    async def generate_flashcards_from_chunks(self, chunks: List[str], num_cards: int = 5) -> Dict[str, Any]:
        """
        Generate flashcards from text chunks using the LLM service.
        
        Args:
            chunks: List of text chunks to generate flashcards from.
            num_cards: Number of flashcards to generate.
            
        Returns:
            Dictionary with generated flashcards.
            
        Raises:
            Exception: If LLM service request fails.
        """
        logger.info(f"Generating {num_cards} flashcards from {len(chunks)} text chunks")
        
        # Prepare request data
        data = {
            "chunks": chunks,
            "num_cards": num_cards
        }
        
        # Send request to LLM service
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/generate/chunks",
                    json=data,
                    timeout=60.0  # 60 seconds timeout
                )
                
                # Check response status
                response.raise_for_status()
                
                # Parse response
                result = response.json()
                logger.info(f"Successfully generated {len(result.get('flashcards', []))} flashcards from chunks")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM service HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LLM service error: {e.response.status_code} - {e.response.text}")
            
        except httpx.RequestError as e:
            logger.error(f"LLM service request error: {str(e)}")
            raise Exception(f"LLM service request error: {str(e)}")
            
        except Exception as e:
            logger.exception(f"Unexpected error during flashcard generation from chunks: {str(e)}")
            raise
