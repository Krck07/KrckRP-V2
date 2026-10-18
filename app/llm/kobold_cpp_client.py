"""
KoboldCpp HTTP Client wrapper for KrckRP.
Supports both streaming narrative generation and synchronous JSON extraction.
"""

import aiohttp
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class KoboldCppClient:
    """
    HTTP client for interacting with KoboldCpp backend.
    
    Provides methods for:
    1. Streaming narrative generation (Narrator)
    2. Synchronous JSON grammar extraction (Extractor)
    3. Fallback mechanisms when KoboldCpp is down
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialize the KoboldCpp client.
        
        Args:
            base_url (str): URL of the KoboldCpp server
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        if not self.session:
            self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    async def is_healthy(self) -> bool:
        """
        Check if KoboldCpp server is reachable and healthy.
        
        Returns:
            bool: True if the server responds properly
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Failed to check KoboldCpp health: {e}")
            return False
            
    async def generate_narrative(self, turn_data: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Generate narrative text using KoboldCpp with streaming.
        
        Args:
            turn_data (Dict): Game state and input data for the turn
            
        Yields:
            str: Chunks of generated narrative text
            
        Raises:
            Exception: If generation fails
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        try:
            # Prepare payload for KoboldCpp
            payload = {
                "prompt": turn_data.get("prompt", ""),
                "max_tokens": turn_data.get("max_tokens", 500),
                "temperature": turn_data.get("temperature", 0.7),
                "stop": ["\n\n"]
            }
            
            # Make streaming request to KoboldCpp
            async with self.session.post(
                f"{self.base_url}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"KoboldCpp generation failed: {response.status}")
                    
                # Stream the response
                async for chunk in response.content.iter_chunked(1024):
                    if chunk:
                        yield chunk.decode('utf-8')
                        
        except Exception as e:
            logger.error(f"Error during narrative generation: {e}")
            raise
            
    async def extract_json(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from text using KoboldCpp's JSON grammar feature.
        
        Args:
            text (str): Text to extract data from
            schema (Dict): JSON schema for extraction
            
        Returns:
            Dict: Extracted structured data
            
        Raises:
            Exception: If extraction fails
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
            
        try:
            # Prepare payload for extraction  
            payload = {
                "prompt": text,
                "grammar": schema,
                "max_tokens": 200
            }
            
            # Make synchronous request to KoboldCpp
            async with self.session.post(
                f"{self.base_url}/extract",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status != 200:
                    raise Exception(f"KoboldCpp extraction failed: {response.status}")
                    
                result = await response.json()
                return result.get("data", {})
                
        except Exception as e:
            logger.error(f"Error during JSON extraction: {e}")
            raise

    async def fallback_generate_narrative(self, turn_data: Dict[str, Any]) -> str:
        """
        Fallback implementation for narrative generation when KoboldCpp is down.
        
        Args:
            turn_data (Dict): Game state and input data
            
        Returns:
            str: Generated fallback narrative
        """
        logger.warning("Using fallback narrative generation")
        # This could implement a simpler logic or use mock LLM 
        return "Fallback narrative generated due to KoboldCpp unavailability."

    async def fallback_extract_json(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback implementation for JSON extraction when KoboldCpp is down.
        
        Args:
            text (str): Text to extract from
            schema (Dict): JSON schema
            
        Returns:
            Dict: Extracted data with fallback values
        """
        logger.warning("Using fallback JSON extraction")
        # Return a minimal valid structure as fallback 
        return {"fallback": True, "extracted_text": text[:100] + "..."}