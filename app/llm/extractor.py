"""
Extractor module for KrckRP.
Handles synchronous JSON grammar extraction from narrative text.
"""

import json
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Extractor:
    """
    Handles structured data extraction from narrative text using JSON grammar.
    
    This class is designed to work with KoboldCpp's JSON grammar feature,
    but can be extended for other extraction methods.
    """
    
    def __init__(self):
        """Initialize the extractor."""
        # Define default schemas for different types of extractions
        self.schemas = {
            "game_state": {
                "type": "object",
                "properties": {
                    "character_name": {"type": "string"},
                    "location": {"type": "string"},
                    "health": {"type": "integer"},
                    "inventory": {"type": "array", "items": {"type": "string"}},
                    "actions": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["character_name", "location"]
            },
            "dialogue": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string"},
                    "text": {"type": "string"},
                    "emotions": {"type": "array", "items": {"type": "string"}},
                    "responses": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["speaker", "text"]
            }
        }
    
    async def extract_structured_data(self, narrative_text: str, turn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from the narrative text using JSON grammar.
        
        Args:
            narrative_text (str): The generated narrative text
            turn_data (Dict): Original turn data
            
        Returns:
            Dict: Structured extraction result
        """
        try:
            # Determine which schema to use based on context
            schema_name = self._get_extraction_schema(turn_data)
            schema = self.schemas.get(schema_name, self.schemas["game_state"])
            
            # In a real implementation, this would call the KoboldCpp client's extract method
            # For now we're simulating with simple parsing
            
            result = await self._extract_with_grammar(narrative_text, schema)
            return {
                "extraction_type": schema_name,
                "data": result,
                "original_narrative": narrative_text[:200] + ("..." if len(narrative_text) > 200 else "")
            }
            
        except Exception as e:
            logger.error(f"Failed to extract structured data: {e}")
            # Return fallback structure in case of failure
            return {
                "extraction_type": "fallback",
                "data": {"error": str(e)},
                "original_narrative": narrative_text[:200] + ("..." if len(narrative_text) > 200 else "")
            }
    
    async def _extract_with_grammar(self, text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate extraction using JSON grammar (would connect to KoboldCpp in real implementation).
        
        Args:
            text (str): Text to extract from
            schema (Dict): JSON schema to validate against
            
        Returns:
            Dict: Extracted data matching the schema
        """
        # In a real implementation, this would call the KoboldCpp client's extract method.
        # For now we return a mock structure that matches the schema.
        
        # Simple example of structured extraction logic
        extracted = {}
        
        if "character" in text.lower():
            extracted["character_name"] = "Hero"
            
        if "location" in text.lower():
            extracted["location"] = "Forest"
            
        if "health" in text.lower():
            extracted["health"] = 100
            
        # Add some generic fields
        extracted["actions"] = ["move", "explore"]
        extracted["inventory"] = ["sword", "potion"]
        
        return extracted
    
    def _get_extraction_schema(self, turn_data: Dict[str, Any]) -> str:
        """
        Determine which extraction schema to use based on the game context.
        
        Args:
            turn_data (Dict): The original turn data
            
        Returns:
            str: Name of the appropriate schema
        """
        # This could be more sophisticated based on game state or turn type
        return "game_state"