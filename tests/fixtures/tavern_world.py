"""
Sample tavern world fixture for testing purposes.
This creates a basic world with campaign, session and entities to test the database models.
"""

import uuid
from datetime import datetime
from sqlmodel import create_engine, Session
from app.models.database_models import World, Campaign, Session as SessionModel, Character, Location, Item


def create_tavern_world_fixture():
    """
    Create a sample tavern world fixture for testing purposes.
    Returns the IDs of created entities to help with testing.
    """
    # Create engine and tables (this is just for testing)
    engine = create_engine("sqlite:///:memory:", echo=True)
    
    # Create all tables
    from app.models.database_models import SQLModel
    SQLModel.metadata.create_all(engine)
    
    # Start a session
    with Session(engine) as session:
        # Create World
        world = World(
            name="The Tavern World",
            description="A fantasy world centered around taverns and adventures"
        )
        session.add(world)
        session.commit()
        session.refresh(world)
        
        # Create Campaign
        campaign = Campaign(
            name="The Rusty Mug Adventure",
            description="An adventure in the famous Rusty Mug tavern",
            world_id=world.id,
            world_clock=datetime.utcnow()  # Added as required
        )
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        
        # Create Session
        session_model = SessionModel(
            name="Session 1: The Beginning",
            description="First session of the adventure",
            campaign_id=campaign.id
        )
        session.add(session_model)
        session.commit()
        session.refresh(session_model)
        
        # Create Characters
        character1 = Character(
            name="Gorak the Brave",
            description="A brave warrior seeking fortune and glory",
            campaign_id=campaign.id
        )
        session.add(character1)
        session.commit()
        session.refresh(character1)
        
        character2 = Character(
            name="Lyra the Wise",
            description="A cunning rogue with a mysterious past",
            campaign_id=campaign.id
        )
        session.add(character2)
        session.commit()
        session.refresh(character2)
        
        # Create Locations
        location1 = Location(
            name="The Rusty Mug Tavern",
            description="The most famous tavern in town, known for its ale and stories",
            campaign_id=campaign.id
        )
        session.add(location1)
        session.commit()
        session.refresh(location1)
        
        location2 = Location(
            name="The Old Mill",
            description="An abandoned mill on the outskirts of town",
            campaign_id=campaign.id
        )
        session.add(location2)
        session.commit()
        session.refresh(location2)
        
        # Create Items
        item1 = Item(
            name="Sword of Light",
            description="A legendary blade that glows with divine power",
            campaign_id=campaign.id
        )
        session.add(item1)
        session.commit()
        session.refresh(item1)
        
        item2 = Item(
            name="Potion of Healing",
            description="Restores health to the drinker",
            campaign_id=campaign.id
        )
        session.add(item2)
        session.commit()
        session.refresh(item2)
        
        # Return IDs for testing
        return {
            "world_id": world.id,
            "campaign_id": campaign.id,
            "session_id": session_model.id,
            "character_ids": [character1.id, character2.id],
            "location_ids": [location1.id, location2.id],
            "item_ids": [item1.id, item2.id]
        }