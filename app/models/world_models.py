"""
World Models for KrckRP.
Defines the structure and schema for world templates that can be used to start campaigns.
"""

from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

class WorldTemplate:
    """Represents a world template that can be used to create campaigns."""
    
    def __init__(self, 
                 name: str,
                 description: str = "",
                 tone: Dict[str, Any] = None,
                 factions: List[Dict[str, Any]] = None,
                 locations: List[Dict[str, Any]] = None,
                 characters: List[Dict[str, Any]] = None,
                 abilities: List[Dict[str, Any]] = None,
                 rules: Dict[str, Any] = None,
                 id: Optional[uuid.UUID] = None,
                 created_at: Optional[datetime] = None):
        self.id = id or uuid.uuid4()
        self.name = name
        self.description = description
        self.tone = tone or {}
        self.factions = factions or []
        self.locations = locations or []
        self.characters = characters or []
        self.abilities = abilities or []
        self.rules = rules or {}
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world object to dictionary for storage."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "tone": self.tone,
            "factions": self.factions,
            "locations": self.locations,
            "characters": self.characters,
            "abilities": self.abilities,
            "rules": self.rules,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldTemplate':
        """Create world object from dictionary."""
        return cls(
            id=uuid.UUID(data["id"]) if data.get("id") else None,
            name=data["name"],
            description=data.get("description", ""),
            tone=data.get("tone", {}),
            factions=data.get("factions", []),
            locations=data.get("locations", []),
            characters=data.get("characters", []),
            abilities=data.get("abilities", []),
            rules=data.get("rules", {}),
        )
    
    def __repr__(self):
        return f"WorldTemplate(id={self.id}, name='{self.name}')"


# Schema for world templates
WORLD_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "format": "uuid"},
        "name": {"type": "string"},
        "description": {"type": "string"},
        "tone": {"type": "object"},
        "factions": {"type": "array", "items": {"type": "object"}},
        "locations": {"type": "array", "items": {"type": "object"}},
        "characters": {"type": "array", "items": {"type": "object"}},
        "abilities": {"type": "array", "items": {"type": "object"}},
        "rules": {"type": "object"},
        "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["name"]
}