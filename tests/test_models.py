import pytest
from sqlmodel import create_engine, Session
from app.models.database_models import World, Campaign, Session as SessionModel


def test_world_model():
    """Test that the World model works correctly."""
    engine = create_engine("sqlite:///:memory:")
    
    from app.models.database_models import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        world = World(
            name="Test World",
            description="A test world for testing purposes"
        )
        session.add(world)
        session.commit()
        session.refresh(world)
        
        assert world.name == "Test World"
        assert world.description == "A test world for testing purposes"


def test_campaign_model():
    """Test that the Campaign model works correctly."""
    engine = create_engine("sqlite:///:memory:")
    
    from app.models.database_models import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # First create a world
        world = World(
            name="Test World",
            description="A test world for testing purposes"
        )
        session.add(world)
        session.commit()
        session.refresh(world)
        
        # Create campaign
        campaign = Campaign(
            name="Test Campaign",
            description="A test campaign for testing purposes",
            world_id=world.id,
            world_clock="2023-01-01 12:00:00"
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        
        assert campaign.name == "Test Campaign"
        assert campaign.description == "A test campaign for testing purposes"
        assert campaign.world_id == world.id


def test_session_model():
    """Test that the Session model works correctly."""
    engine = create_engine("sqlite:///:memory:")
    
    from app.models.database_models import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # First create a world and campaign
        world = World(
            name="Test World",
            description="A test world for testing purposes"
        )
        session.add(world)
        session.commit()
        session.refresh(world)
        
        campaign = Campaign(
            name="Test Campaign",
            description="A test campaign for testing purposes",
            world_id=world.id,
            world_clock="2023-01-01 12:00:00"
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        
        # Create session
        session_model = SessionModel(
            name="Test Session",
            description="A test session for testing purposes",
            campaign_id=campaign.id
        )
        session.add(session_model)
        session.commit()
        session.refresh(session_model)
        
        assert session_model.name == "Test Session"
        assert session_model.description == "A test session for testing purposes"


def test_fixture_creation():
    """Test that the tavern world fixture can be created."""
    from tests.fixtures.tavern_world import create_tavern_world_fixture
    
    # This just verifies it doesn't crash
    result = create_tavern_world_fixture()
    
    assert "world_id" in result
    assert "campaign_id" in result
    assert "session_id" in result
    assert len(result["character_ids"]) == 2
    assert len(result["location_ids"]) == 2
    assert len(result["item_ids"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])