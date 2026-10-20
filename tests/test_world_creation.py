"""
Tests for World Creation API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient
from app.api.main import app
from app.models.world_models import World

# Initialize test client
client = TestClient(app)

@pytest.fixture
def mock_kobold_client():
    """Mock KoboldCpp client for testing."""
    with patch('app.api.world_creation.kobold_client') as mock:
        yield mock

@pytest.fixture
def mock_extractor():
    """Mock Extractor for testing.""" 
    with patch('app.api.world_creation.extractor') as mock:
        yield mock

@pytest.fixture
def mock_db_manager():
    """Mock DatabaseManager for testing."""
    with patch('app.models.database_models.DatabaseManager') as mock:
        yield mock

class TestWorldCreationAPI:
    
    def test_create_world_endpoint_exists(self):
        """Test that the world creation endpoint exists and is accessible."""
        response = client.post("/world/create", json={"prompt": "Create a fantasy world"})
        assert response.status_code in [200, 400, 500]  # Could be any valid status
        
    def test_chat_with_world_builder_endpoint_exists(self):
        """Test that the world chat endpoint exists and is accessible."""
        response = client.post("/world/chat", json={"message": "Tell me about a fantasy world"})
        assert response.status_code in [200, 400, 500]  # Could be any valid status
        
    def test_validate_world_structure_endpoint_exists(self):
        """Test that the world validation endpoint exists and is accessible."""
        response = client.post("/world/validate", json={"name": "Test World"})
        assert response.status_code in [200, 400]  # Should return success or error
        
    @pytest.mark.asyncio
    async def test_world_creation_flow(self, mock_kobold_client, mock_extractor, mock_db_manager):
        """Test the full world creation flow with mocked dependencies."""
        
        # Setup mocks 
        mock_kobold_client.generate_narrative = AsyncMock(return_value=["Generated narrative"])
        mock_extractor.extract_structured_data = AsyncMock(
            return_value={
                "extraction_type": "world_creation",
                "data": {
                    "world_name": "Test Fantasy World",
                    "world_description": "A magical realm with dragons and wizards", 
                    "tone": {"genre": "fantasy", "mood": "epic"},
                    "factions": [{"name": "The Kingdom", "alignment": "neutral"}],
                    "locations": [{"name": "Dragon's Peak", "size": "large"}],
                    "characters": [{"name": "Sir Galahad", "role": "knight"}],
                    "ability_groups": [{"name": "Combat", "skinned_name": "Swordplay"}],
                    "world_rules": {"combat_system": "traditional"}
                }
            }
        )
        mock_db_manager.create_world = Mock(return_value="test-world-id")
        
        # Test the endpoint
        response = client.post("/world/create", json={
            "prompt": "Create a fantasy world with dragons",
            "campaign_id": "test-campaign"
        })
        
        assert response.status_code == 200
        
    def test_world_validation(self):
        """Test that world validation works correctly."""
        # Test valid world structure
        valid_world = {
            "name": "Valid World",
            "description": "A valid description" 
        }
        
        response = client.post("/world/validate", json=valid_world)
        assert response.status_code == 200
        
    def test_world_validation_invalid(self):
        """Test that invalid world structure is rejected."""
        # Test missing required field
        invalid_world = {
            "description": "Missing name"
        }
        
        response = client.post("/world/validate", json=invalid_world)
        assert response.status_code == 400

class TestWorldModel:
    
    def test_world_creation(self):
        """Test creating a World object."""
        world_data = {
            "name": "Test World",
            "description": "A test world for testing",
            "tone": {"genre": "fantasy", "mood": "epic"},
            "factions": [{"name": "The Kingdom"}],
            "locations": [{"name": "Castle Town"}],
            "characters": [{"name": "Hero"}],
            "abilities": [{"name": "Combat"}],
            "rules": {"combat_system": "traditional"}
        }
        
        world = World(**world_data)
        
        assert world.name == "Test World"
        assert world.description == "A test world for testing"
        assert world.tone["genre"] == "fantasy"
        assert len(world.factions) == 1
        
    def test_world_to_dict(self):
        """Test converting World to dictionary."""
        world = World(
            name="Test World",
            description="Test description"
        )
        
        data = world.to_dict()
        assert data["name"] == "Test World"
        assert data["description"] == "Test description"
        
    def test_world_from_dict(self):
        """Test creating World from dictionary."""
        world_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "From Dict Test", 
            "description": "Test description",
            "tone": {},
            "factions": [],
            "locations": [],
            "characters": [],
            "abilities": [],
            "rules": {},
            "created_at": "2023-01-01T00:00:00"
        }
        
        world = World.from_dict(world_data)
        assert world.name == "From Dict Test"

if __name__ == "__main__":
    pytest.main([__file__])