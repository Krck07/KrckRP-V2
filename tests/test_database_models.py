"""
Test cases for database models in KrckRP.
"""

import pytest
from sqlmodel import create_engine, Session
from app.models.database_models import (
    World, Campaign, Session as SessionModel, Character, Location, 
    Item, Faction, Ability, Quest, Summary, Relationship, EventLog, GameTurn
)
import uuid
from datetime import datetime, timezone


def test_world_model_creation():
    """Test that World model can be created and saved."""
    # Create a test database in memory
    engine = create_engine("sqlite:///:memory:")
    
    # Create tables
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        world = World(
            id=uuid.uuid4(),
            name="Test World",
            description="A test world for testing purposes",
            tone="{}",
            factions="[]",
            locations="[]", 
            characters="[]",
            abilities="[]",
            rules="{}"
        )
        
        session.add(world)
        session.commit()
        
        # Verify it was saved
        retrieved_world = session.get(World, world.id)
        assert retrieved_world is not None
        assert retrieved_world.name == "Test World"


def test_campaign_model_creation():
    """Test that Campaign model can be created."""
    engine = create_engine("sqlite:///:memory:")
    
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Create a world first
        world = World(
            id=uuid.uuid4(),
            name="Test World",
            description="A test world"
        )
        session.add(world)
        session.commit()
        
        campaign = Campaign(
            id=uuid.uuid4(),
            world_id=world.id,
            name="Test Campaign",
            description="A test campaign"
        )
        
        session.add(campaign)
        session.commit()
        
        # Verify it was saved
        retrieved_campaign = session.get(Campaign, campaign.id)
        assert retrieved_campaign is not None
        assert retrieved_campaign.name == "Test Campaign"


def test_character_model_creation():
    """Test that Character model can be created."""
    engine = create_engine("sqlite:///:memory:")
    
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        campaign = Campaign(
            id=uuid.uuid4(),
            world_id=uuid.uuid4(),
            name="Test Campaign",
            description="A test campaign"
        )
        session.add(campaign)
        session.commit()
        
        character = Character(
            id=uuid.uuid4(),
            name="Test Character",
            description="A test character",
            campaign_id=campaign.id
        )
        
        session.add(character)
        session.commit()
        
        # Verify it was saved
        retrieved_character = session.get(Character, character.id)
        assert retrieved_character is not None
        assert retrieved_character.name == "Test Character"


def test_database_manager():
    """Test the DatabaseManager class functionality."""
    engine = create_engine("sqlite:///:memory:")
    
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    # Test that we can instantiate the manager without errors
    from app.models.database_models import DatabaseManager
    
    db_manager = DatabaseManager(database_url="sqlite:///:memory:")
    assert db_manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])