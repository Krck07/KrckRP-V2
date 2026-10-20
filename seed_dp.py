import uuid
from sqlmodel import Session, create_engine
# Adjust these imports based on your actual file structure
from app.models.database_models import engine, World, Campaign, Character, Location, Item

def seed():
    # Create tables first
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 1. Create a World template
        world = World(
            id=uuid.uuid4(),
            name="Test World", 
            description="A generic fantasy testing realm.",
            tone="{}",
            factions="[]",
            locations="[]",
            characters="[]",
            abilities="[]",
            rules="{}"
        )
        session.add(world)
        session.commit() # Commit to generate the world.id

        # 2. Create a Campaign using that World
        campaign = Campaign(
            id=uuid.uuid4(),
            world_id=world.id,
            name="Test Campaign",
            description="A sample campaign for testing purposes.",
        )
        session.add(campaign)
        session.commit()
        
        # 3. Create a starting Location 
        location = Location(
            id=uuid.uuid4(),
            name="Forest Clearing",
            description="A peaceful clearing in the middle of an ancient forest, where travelers often rest.",
            campaign_id=campaign.id
        )
        session.add(location)
        session.commit()
        
        # 4. Create a Player Character (with stats)
        character = Character(
            id=uuid.uuid4(),
            name="Hero",
            description="A brave adventurer with potential for great deeds.",
            campaign_id=campaign.id
        )
        session.add(character)
        session.commit()
        
        # 5. Create an Item in their inventory
        item = Item(
            id=uuid.uuid4(),
            name="Iron Sword",
            description="A sturdy iron sword, well-maintained and ready for battle.",
            campaign_id=campaign.id
        )
        session.add(item)
        session.commit()
        
    print("Database seeded successfully with minimum required starting data!")

if __name__ == "__main__":
    seed()