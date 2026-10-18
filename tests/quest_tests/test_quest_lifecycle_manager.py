"""
Tests for QuestLifecycleManager functionality.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

# Import the module we're testing
from app.engine.quest_lifecycle_manager import QuestLifecycleManager
from app.models.database_models import DatabaseManager


class TestQuestLifecycleManager:
    """Test cases for QuestLifecycleManager."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_manager = MagicMock()
        self.quest_manager = QuestLifecycleManager(self.mock_db_manager)
    
    @pytest.mark.asyncio
    async def test_handle_extractor_events_with_proposed_quests(self):
        """Test handling of proposed quests from extractor."""
        turn_data = {
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "proposed_quests": [
                {
                    "title": "Find the Lost Artifact",
                    "summary": "The player needs to find a mysterious artifact in the ancient ruins.",
                    "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
        
        # Mock the database call
        self.mock_db_manager.create_quest = AsyncMock()
        
        result = await self.quest_manager.handle_extractor_events(turn_data, extraction_result)
        
        assert "proposed_quests" in result
        
    @pytest.mark.asyncio 
    async def test_handle_extractor_events_with_quest_updates(self):
        """Test handling of quest updates from extractor."""
        turn_data = {
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "quest_updates": [
                {
                    "quest_id": "123e4567-e89b-12d3-a456-426614174001",
                    "status": "active"
                }
            ]
        }
        
        # Mock the database call
        self.mock_db_manager.update_quest_status = AsyncMock()
        
        result = await self.quest_manager.handle_extractor_events(turn_data, extraction_result)
        
        assert "quest_updates" in result
        
    @pytest.mark.asyncio
    async def test_handle_extractor_events_with_completed_quests(self):
        """Test handling of completed quests from extractor."""
        turn_data = {
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "completed_quests": [
                {
                    "quest_id": "123e4567-e89b-12d3-a456-426614174001"
                }
            ]
        }
        
        # Mock the database call
        self.mock_db_manager.update_quest_status = AsyncMock()
        
        result = await self.quest_manager.handle_extractor_events(turn_data, extraction_result)
        
        assert "completed_quests" in result
        
    @pytest.mark.asyncio
    async def test_handle_extractor_events_with_failed_quests(self):
        """Test handling of failed quests from extractor."""
        turn_data = {
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "failed_quests": [
                {
                    "quest_id": "123e4567-e89b-12d3-a456-426614174001"
                }
            ]
        }
        
        # Mock the database call
        self.mock_db_manager.update_quest_status = AsyncMock()
        
        result = await self.quest_manager.handle_extractor_events(turn_data, extraction_result)
        
        assert "failed_quests" in result
        
    @pytest.mark.asyncio
    async def test_handle_extractor_events_no_events(self):
        """Test handling of extractor events when there are no quest-related events."""
        turn_data = {
            "campaign_id": "123e4567-e89b-12d3-a456-426614174000"
        }
        
        extraction_result = {
            "characters": ["Alice", "Bob"],
            "locations": ["Forest", "Castle"]
        }
        
        result = await self.quest_manager.handle_extractor_events(turn_data, extraction_result)
        
        # Should return the same structure
        assert result == extraction_result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])