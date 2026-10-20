"""
Database models for KrckRP engine.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
import json
import logging
from uuid import UUID
logger = logging.getLogger(__name__)


# Base classes and relationships
class World(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    tone: Optional[str] = None  # JSON string of the tone data
    factions: Optional[str] = None  # JSON string of factions list
    locations: Optional[str] = None  # JSON string of locations list
    characters: Optional[str] = None  # JSON string of characters list
    abilities: Optional[str] = None  # JSON string of ability groups list
    rules: Optional[str] = None  # JSON string of world rules
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Campaign(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    world_id: uuid.UUID = Field(foreign_key="world.id")
    name: str
    description: str
    world_clock: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Session(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    name: str
    description: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None  # When session officially begins
    ended_at: Optional[datetime] = None   # When session ends


class Character(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Location(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Item(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Faction(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ability(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Quest(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    name: str
    description: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Summary(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    content: str
    campaign_id: uuid.UUID = Field(foreign_key="campaign.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Relationship(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    character_id: uuid.UUID = Field(foreign_key="character.id")
    related_character_id: uuid.UUID = Field(foreign_key="character.id")
    relationship_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GameTurn(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default=None, primary_key=True)
    turn_id: int
    timestamp: datetime
    prompt: str
    narrative: str
    extraction_data: str  # JSON string of the extracted data
    status: str 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    campaign_id: Optional[uuid.UUID] = Field(foreign_key="campaign.id")


engine = create_engine("sqlite:///./test.db", echo=True)


class DatabaseManager:
    def __init__(self, database_url: str = "sqlite:///./test.db"):
        """Initialize the database manager with a connection."""
        self.engine = create_engine(database_url, echo=True)
        
    async def log_event(self, event_log: EventLog) -> None:
        """
        Log an event to the EventLog table.
        
        Args:
            event_log (EventLog): The event to log
        """
        try:
            with Session(self.engine) as session:
                session.add(event_log)
                session.commit()
        except Exception as e:
            logger.error(f"Error logging event: {e}")
            raise
        
    async def get_events_for_session(self, session_id: UUID) -> List[EventLog]:
        """
        Get all events for a specific session.
        
        Args:
            session_id (UUID): The session ID to query
            
        Returns:
            List[EventLog]: The list of event logs
        """
        try:
            with Session(self.engine) as session:
                statement = SQLModel.select(EventLog).where(EventLog.session_id == session_id)
                result = session.exec(statement)
                return result.all()
        except Exception as e:
            logger.error(f"Error retrieving events: {e}")
            raise
        
    async def create_tables(self) -> None:
        """
        Create all database tables.
        """
        try:
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise