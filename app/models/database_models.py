"""
Database models for KrckRP engine.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session


# Base classes and relationships
class World(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Campaign(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    world_id: uuid.UUID = Field(foreign_key="world.id")
    name: str
    description: str
    world_clock: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Session(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    name: str
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Character(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Location(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Item(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Faction(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Ability(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Quest(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Summary(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    content: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Relationship(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    character_id: uuid.UUID = Field(foreign_key="character.id")
    related_character_id: uuid.UUID = Field(foreign_key="character.id")
    relationship_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EventLog(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    turn_id: int
    session_id: uuid.UUID  # Link to the session
    entity_type: str  # e.g., 'Character', 'Location', etc.
    entity_id: uuid.UUID  
    field: str  # The specific field being changed
    operation: str  # e.g., 'UPDATE', 'INSERT', 'DELETE'
    before_value: Optional[str] = None  # JSON string representation of the value before change
    after_value: Optional[str] = None   # JSON string representation of the value after change
    sequence_num: int  # Order within a turn (for multiple changes to same entity)
    witness_metadata: str  # Additional context about who/when changed it
    created_at: datetime = Field(default_factory=datetime.utcnow)


class GameTurn(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    turn_id: int
    timestamp: datetime
    prompt: str
    narrative: str
    extraction_data: str  # JSON string of the extracted data
    status: str 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    campaign_id: Optional[uuid.UUID] = Field(foreign_key="campaign.id")


class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///./test.db"):
        """Initialize the database manager with a connection."""
        self.engine = create_engine(database_url, echo=True)
        
    async def cleanup_session_entries(self, session_id: uuid.UUID) -> None:
        """
        Cleanup vector entries associated with a specific session.
        This is called as part of the rollback mechanism when sessions are rewound.
        
        Args:
            session_id (uuid.UUID): The session ID to clean up
        """
        from app.memory.semantic_memory import SemanticMemoryManager
        semantic_manager = SemanticMemoryManager(self)
        await semantic_manager.delete_session_entries(session_id)
        
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

    async def get_recent_turns(self, campaign_id: uuid.UUID, limit: int = 10) -> List[GameTurn]:
        """
        Retrieve recent game turns for a campaign.
        
        Args:
            campaign_id (uuid.UUID): The campaign ID to query
            limit (int): Maximum number of turns to retrieve
            
        Returns:
            List[GameTurn] ordered by turn_id ascending
        """
        with Session(self.engine) as session:
            result = session.query(GameTurn).filter(
                GameTurn.campaign_id == campaign_id,
                GameTurn.turn_id > 0
            ).order_by(GameTurn.turn_id.asc()).limit(limit)
            
            return list(result)
    
    async def get_recent_turns_with_details(self, campaign_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent game turns for a campaign with detailed information.
        
        Args:
            campaign_id (uuid.UUID): The campaign ID to query
            limit (int): Maximum number of turns to retrieve
            
        Returns:
            List[Dict] containing turn details including prompt and extraction data
        """
        try:
            with Session(self.engine) as session:
                result = session.query(GameTurn).filter(
                    GameTurn.campaign_id == campaign_id,
                    GameTurn.turn_id > 0
                ).order_by(GameTurn.turn_id.asc()).limit(limit)
                
                turns_data = []
                for turn in result:
                    try:
                        extraction_data = json.loads(turn.extraction_data) if turn.extraction_data else {}
                    except (json.JSONDecodeError, TypeError):
                        extraction_data = {}
                    
                    turns_data.append({
                        "turn_id": turn.turn_id,
                        "timestamp": turn.timestamp.isoformat() if turn.timestamp else None,
                        "prompt": turn.prompt,
                        "narrative": turn.narrative,
                        "extraction_data": extraction_data
                    })
                
                return turns_data
        except Exception as e:
            logger.error(f"Error retrieving recent turns with details: {e}")
            return []            
    async def get_summary_by_campaign(self, campaign_id: uuid.UUID) -> Optional[Summary]:
        """
        Retrieve the most recent summary for a campaign.
        
        Args:
            campaign_id (uuid.UUID): The campaign ID to query
            
        Returns:
            Summary object or None if not found
        """
        with Session(self.engine) as session:
            return session.query(Summary).filter(Summary.campaign_id == campaign_id).order_by(Summary.created_at.desc()).first()
    async def get_all_turns(self) -> List[GameTurn]:
        """
        Retrieve all game turns from the database.
        
        Returns:
            List of GameTurn objects
        """
        with Session(self.engine) as session:
            return session.query(GameTurn).all()
            
    async def get_all_campaigns(self) -> List[Campaign]:
        """
        Retrieve all campaigns from the database.
        
        Returns:
            List of Campaign objects
        """
        with Session(self.engine) as session:
            return session.query(Campaign).all()
            
    async def get_campaign(self, campaign_id: uuid.UUID) -> Optional[Campaign]:
        """
        Retrieve a specific campaign from the database.
        
        Args:
            campaign_id (uuid.UUID): The ID of the campaign to retrieve
            
        Returns:
            Campaign or None if not found
        """
        with Session(self.engine) as session:
            return session.query(Campaign).filter(Campaign.id == campaign_id).first()
            
    async def create_campaign(self, name: str, description: str = '') -> uuid.UUID:
        """
        Create a new campaign in the database.
        
        Args:
            name (str): Name of the campaign
            description (str): Description of the campaign
            
        Returns:
            UUID of the created campaign
        """
        # For now we'll create with a default world ID, but in reality this should be parameterized
        world_id = uuid.uuid4()  # This is a simplified approach for demo purposes
        
        campaign = Campaign(
            name=name,
            description=description,
            world_id=world_id
        )
        
        with Session(self.engine) as session:
            session.add(campaign)
            session.commit()
            session.refresh(campaign)
            return campaign.id
            
    async def get_characters_by_campaign(self, campaign_id: uuid.UUID) -> List[Character]:
        """
        Get all characters associated with a specific campaign.
        
        Args:
            campaign_id (uuid.UUID): The ID of the campaign
            
        Returns:
            List of Character objects
        """
        with Session(self.engine) as session:
            return session.query(Character).filter(Character.campaign_id == campaign_id).all()
            
    async def get_locations_by_campaign(self, campaign_id: uuid.UUID) -> List[Location]:
        """
        Get all locations associated with a specific campaign.
        
        Args:
            campaign_id (uuid.UUID): The ID of the campaign
            
        Returns:
            List of Location objects
        """
        with Session(self.engine) as session:
            return session.query(Location).filter(Location.campaign_id == campaign_id).all()
            
    async def get_items_by_campaign(self, campaign_id: uuid.UUID) -> List[Item]:
        """
        Get all items associated with a specific campaign.
        
        Args:
            campaign_id (uuid.UUID): The ID of the campaign
            
        Returns:
            List of Item objects
        """
        with Session(self.engine) as session:
            return session.query(Item).filter(Item.campaign_id == campaign_id).all()
            
    async def get_quests_by_campaign(self, campaign_id: uuid.UUID) -> List[Quest]:
        """
        Get all quests associated with a specific campaign.
        
        Args:
            campaign_id (uuid.UUID): The ID of the campaign
            
        Returns:
            List of Quest objects
        """
        with Session(self.engine) as session:
            return session.query(Quest).filter(Quest.campaign_id == campaign_id).all()

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