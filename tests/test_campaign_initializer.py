"""
Tests for the Campaign Initializer module.
"""

import pytest
from unittest.mock import Mock, patch
import uuid

from app.engine.campaign_initializer import CampaignInitializer
from app.models.world_models import World
from app.models.database_models import DatabaseManager


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    return Mock(spec=DatabaseManager)


@pytest.fixture
def sample_world_data():
    """Create sample world data for testing."""
    return World(
        name="Test World",
        description="A test world for campaign initialization",
        tone={
            "genre": "fantasy",
            "mood": "adventurous"
        },
        factions=[
            {
                "name": "The Guild of Adventurers",
                "description": "A group of brave adventurers",
                "relations": ["The King's Court"],
                "alignment": "neutral"
            }
        ],
        locations=[
            {
                "name": "The Town Square",
                "description": "Central gathering place in the town",
                "connections": ["The Inn", "The Market"],
                "size": "medium"
            }
        ],
        characters=[
            {
                "name": "Gandalf",
                "description": "A wise wizard",
                "role": "NPC",
                "faction": "The Guild of Adventurers"
            }
        ],
        abilities=[
            {
                "name": "Fireball",
                "description": "A powerful fire spell",
                "skinned_name": "Fire Magic"
            }
        ],
        rules={
            "combat_system": "d20",
            "magic_system": "spells"
        }
    )


@pytest.fixture
def sample_character_data():
    """Create sample character data for testing."""
    return {
        "name": "Player Character",
        "description": "The main player character"
    }


class TestCampaignInitializer:
    
    def test_initialize_campaign_from_world(self, mock_db_manager, sample_world_data, sample_character_data):
        """Test campaign initialization from a world template."""
        
        # Setup mocks
        mock_db_manager.create_campaign.return_value = uuid.uuid4()
        mock_db_manager.save_location = Mock()
        mock_db_manager.save_faction = Mock()
        mock_db_manager.save_character = Mock()
        mock_db_manager.save_ability = Mock()
        mock_db_manager.create_session = Mock(return_value=uuid.uuid4())
        
        # Create initializer
        initializer = CampaignInitializer(mock_db_manager)
        
        # Call the method
        campaign_id = initializer.initialize_campaign_from_world(
            world_template=sample_world_data,
            campaign_name="Test Campaign",
            campaign_description="A test campaign",
            player_character_data=sample_character_data
        )
        
        # Verify calls were made
        mock_db_manager.create_campaign.assert_called_once_with(
            name="Test Campaign",
            description="A test campaign",
            world_id=sample_world_data.id
        )
        
        # The exact number of save operations depends on the actual data in sample_world_data
        
    def test_create_character(self, mock_db_manager, sample_world_data):
        """Test creating a character."""
        # Setup mocks 
        mock_db_manager.save_character = Mock()
        
        initializer = CampaignInitializer(mock_db_manager)
        
        character_data = {
            "name": "New Character",
            "description": "A new character"
        }
        
        # Call method
        result = initializer.create_character(
            campaign_id=uuid.uuid4(),
            character_data=character_data
        )
        
        # Verify the call was made
        mock_db_manager.save_character.assert_called_once()
    
    def test_create_initial_session(self, mock_db_manager):
        """Test creating an initial session."""
        # Setup mocks
        mock_db_manager.save_session = Mock()
        
        initializer = CampaignInitializer(mock_db_manager)
        
        campaign_id = uuid.uuid4()
        
        # Call method
        result = initializer.create_initial_session(campaign_id)
        
        # Verify the call was made
        mock_db_manager.save_session.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])