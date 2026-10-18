"""
Tests for validation and rewind functionality in StateManager.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

# Import the modules we're testing  
from app.engine.state_manager import StateManager, ValidationService
from app.models.database_models import DatabaseManager


class TestValidationAndRewind:
    """Test cases for validation and rewind functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_manager = MagicMock()
        self.validation_service = ValidationService(self.mock_db_manager)
        self.state_manager = StateManager(self.mock_db_manager)
        
    @pytest.mark.asyncio
    async def test_validate_extraction_success(self):
        """Test successful validation of extraction result."""
        turn_data = {"prompt": "test prompt"}
        extraction_result = {
            "characters": ["Alice", "Bob"],
            "locations": ["Forest", "Castle"], 
            "items": ["Sword", "Shield"],
            "factions": ["Knights", "Villagers"]
        }
        
        result = await self.validation_service.validate_extraction(turn_data, extraction_result)
        
        assert result is True
        
    @pytest.mark.asyncio
    async def test_validate_extraction_missing_fields(self):
        """Test validation failure when required fields are missing."""
        turn_data = {"prompt": "test prompt"}
        extraction_result = {
            "characters": ["Alice", "Bob"],
            # Missing locations, items, factions
        }
        
        result = await self.validation_service.validate_extraction(turn_data, extraction_result)
        
        assert result is False
        
    @pytest.mark.asyncio  
    async def test_commit_turn_with_quest_processing(self):
        """Test commit turn with quest lifecycle processing."""
        # This will be a simple mock test to verify our integration works
        turn_data = {
            "prompt": "test prompt", 
            "turn_id": "turn_1234567890",
            "timestamp": "2023-01-01T00:00:00Z",
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "original_narrative": "Test narrative",
            "proposed_quests": [
                {
                    "title": "Find the Lost Artifact", 
                    "summary": "Search for a hidden artifact in ruins.",
                    "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ],
            "characters": ["Alice", "Bob"],
            "locations": ["Forest", "Castle"]
        }
        
        # Mock the database save methods and validation
        self.mock_db_manager.save_turn = AsyncMock()
        self.validation_service.validate_extraction = AsyncMock(return_value=True)
        
        result = await self.state_manager.commit_turn(turn_data, extraction_result)
        
        assert result["status"] == "success"
        assert "extraction_result" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])