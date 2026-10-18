from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Session, create_engine
from datetime import datetime
import uuid
import json


class World(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    world_id: uuid.UUID = Field(foreign_key="world.id")
    name: str
    description: str
    world_clock: datetime = Field(default_factory=datetime.utcnow)  # Added as required
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to World
    world: "World" = Relationship(back_populates="campaigns")


class Session(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    name: str
    description: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="sessions")


class Character(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="characters")


class Location(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="locations")


class Item(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="items")


class Faction(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="factions")


class Ability(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="abilities")


class Quest(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="quests")


class Summary(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Campaign
    campaign: "Campaign" = Relationship(back_populates="summaries")


class Relationship(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    character_id: uuid.UUID = Field(foreign_key="character.id")
    related_character_id: uuid.UUID = Field(foreign_key="character.id")
    relationship_type: str  # e.g., "friend", "enemy", "ally"
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships to Characters
    character: "Character" = Relationship(back_populates="relationships")
    related_character: "Character" = Relationship()


class EventLog(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    turn_id: int  # The game turn number
    entity_type: str  # e.g., "character", "location", etc.
    entity_id: uuid.UUID  # Foreign key to the specific entity
    field: str  # Name of the field that was modified
    operation: str  # create, update, delete
    before_value: Optional[str] = None  # String representation of the old value
    after_value: Optional[str] = None  # String representation of the new value
    sequence_num: int  # Sequence number within a turn for ordering events
    witness_metadata: str  # JSON string containing information about who witnessed the event
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GameTurn(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    turn_id: str  # Unique identifier for the turn
    timestamp: datetime
    prompt: str  # The input prompt used for this turn
    narrative: str  # Generated narrative text
    extraction_data: str  # JSON string of extracted data
    status: str = "pending"  # Status of the turn (pending, completed, failed)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Define relationships for back-population
World.campaigns = Relationship(back_populates="world")
Campaign.sessions = Relationship(back_populates="campaign")
Campaign.characters = Relationship(back_populates="campaign")
Campaign.locations = Relationship(back_populates="campaign")
Campaign.items = Relationship(back_populates="campaign")
Campaign.factions = Relationship(back_populates="campaign")
Campaign.abilities = Relationship(back_populates="campaign")
Campaign.quests = Relationship(back_populates="campaign")
Campaign.summaries = Relationship(back_populates="campaign")
Character.relationships = Relationship(back_populates="character")


# Database manager for handling operations
class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///./test.db"):
        """Initialize the database manager with a connection."""
        self.engine = create_engine(database_url, echo=True)
        
    async def save_turn(self, game_turn: GameTurn) -> None:
        """
        Save a completed game turn to the database.
        
        Args:
            game_turn (GameTurn): The game turn to save
        """
        with Session(self.engine) as session:
            session.add(game_turn)
            session.commit()
            
    async def get_turn(self, turn_id: str) -> Optional[GameTurn]:
        """
        Retrieve a specific game turn from the database.
        
        Args:
            turn_id (str): The unique identifier of the turn
            
        Returns:
            GameTurn or None if not found
        """
        with Session(self.engine) as session:
            return session.query(GameTurn).filter(GameTurn.turn_id == turn_id).first()
            
    async def get_all_turns(self) -> List[GameTurn]:
        """
        Retrieve all game turns from the database.
        
        Returns:
            List of GameTurn objects
        """
        with Session(self.engine) as session:
            return session.query(GameTurn).all()


__all__ = [
    "World",
    "Campaign", 
    "Session",
    "Character",
    "Location",
    "Item",
    "Faction",
    "Ability",
    "Quest",
    "Summary",
    "Relationship",
    "EventLog",
    "GameTurn"
]