"""
Mock LLM for testing and fallback purposes.
"""

import asyncio
from typing import Dict, Any
import random

class MockLLM:
    """
    A mock LLM that can be used when KoboldCpp is not available.
    Provides basic narrative generation and extraction capabilities.
    """

    def __init__(self):
        """Initialize the mock LLM."""
        self.responses = {
            "narrative": [
                "The hero ventures into the mysterious forest, where ancient secrets lie buried.",
                "A dark figure emerges from the shadows, wielding a glowing sword.",
                "The old wizard speaks in riddles, revealing cryptic clues about the quest ahead.",
                "A fierce battle erupts as the party faces off against the terrifying monster.",
                "Through clever negotiation, the group manages to avoid conflict and gain valuable information."
            ],
            "extraction": {
                "character_name": "Hero",
                "location": "Forest",
                "health": 100,
                "inventory": ["sword", "potion"],
                "actions": ["explore", "fight"]
            }
        }

    async def generate_narrative(self, prompt: str) -> str:
        """
        Generate a mock narrative based on the input.
        
        Args:
            prompt (str): The input prompt
            
        Returns:
            str: Generated narrative text
        """
        # Simple response generation - in reality this would be more sophisticated
        return random.choice(self.responses["narrative"])
    
    async def extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract mock structured data from the text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict: Mocked extraction result
        """
        # Return a fixed structure for now - this would be more complex in reality
        return self.responses["extraction"]

# Create a global instance for easy access
mock_llm = MockLLM()