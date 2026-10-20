"""
Campaign Initializer for KrckRP.
This module handles the creation of campaign data from world templates,
including instantiation of Locations, Factions, Characters, etc. for Turn 1.
"""

from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from app.models.database_models import (
    World, Campaign, Character, Location, Item, Faction, Ability, Quest, 
    Relationship, Session
)
from app.models.world_models import World as WorldModel


class CampaignInitializer:
    """Handles initialization of campaign data from world templates."""
    
    def __init__(self, db_manager):
        """
        Initialize the campaign initializer with a database manager.
        
        Args:
            db_manager: Instance of DatabaseManager for database operations
        """
        self.db_manager = db_manager
    
    def initialize_campaign_from_world(
        self,
        world_template: WorldModel,
        campaign_name: str,
        campaign_description: str = "",
        player_character_data: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Initialize a new campaign from a world template.
        
        Args:
            world_template: The world template to base the campaign on
            campaign_name: Name for the new campaign
            campaign_description: Description of the campaign
            player_character_data: Data for creating the player character
            
        Returns:
            UUID of the created campaign
        """
        # Create the campaign first
        campaign_id = self.db_manager.create_campaign(
            name=campaign_name,
            description=campaign_description,
            world_id=world_template.id
        )
        
        # Initialize all entities from the world template
        self._create_locations_from_world(campaign_id, world_template)
        self._create_factions_from_world(campaign_id, world_template)
        self._create_characters_from_world(campaign_id, world_template, player_character_data)
        self._create_abilities_from_world(campaign_id, world_template)
        
        # Create a default session for the campaign
        session_id = self.db_manager.create_session(
            name="Initial Session",
            description="Session created at campaign start",
            campaign_id=campaign_id
        )
        
        return campaign_id
    
    def _create_locations_from_world(self, campaign_id: uuid.UUID, world_template: WorldModel):
        """Create locations from the world template."""
        if not world_template.locations:
            return
            
        for location_data in world_template.locations:
            try:
                # Create location
                location = Location(
                    name=location_data.get('name', 'Unnamed Location'),
                    description=location_data.get('description', ''),
                    campaign_id=campaign_id
                )
                
                self.db_manager.save_location(location)
                
                # If location has connections, we'll need to handle those separately
                
            except Exception as e:
                print(f"Error creating location {location_data.get('name', 'Unnamed')}: {e}")
    
    def _create_factions_from_world(self, campaign_id: uuid.UUID, world_template: WorldModel):
        """Create factions from the world template."""
        if not world_template.factions:
            return
            
        for faction_data in world_template.factions:
            try:
                # Create faction
                faction = Faction(
                    name=faction_data.get('name', 'Unnamed Faction'),
                    description=faction_data.get('description', ''),
                    campaign_id=campaign_id
                )
                
                self.db_manager.save_faction(faction)
                
            except Exception as e:
                print(f"Error creating faction {faction_data.get('name', 'Unnamed')}: {e}")
    
    def _create_characters_from_world(self, campaign_id: uuid.UUID, world_template: WorldModel, 
                                    player_character_data: Optional[Dict[str, Any]] = None):
        """Create characters from the world template and optionally add a player character."""
        # First create any NPCs from the world template
        if world_template.characters:
            for char_data in world_template.characters:
                try:
                    character = Character(
                        name=char_data.get('name', 'Unnamed NPC'),
                        description=char_data.get('description', ''),
                        campaign_id=campaign_id
                    )
                    
                    self.db_manager.save_character(character)
                except Exception as e:
                    print(f"Error creating character {char_data.get('name', 'Unnamed')}: {e}")
        
        # Then create the player character if provided
        if player_character_data:
            try:
                player_char = Character(
                    name=player_character_data.get('name', 'Player Character'),
                    description=player_character_data.get('description', ''),
                    campaign_id=campaign_id
                )
                
                self.db_manager.save_character(player_char)
                
            except Exception as e:
                print(f"Error creating player character: {e}")
    
    def _create_abilities_from_world(self, campaign_id: uuid.UUID, world_template: WorldModel):
        """Create abilities from the world template."""
        if not world_template.abilities:
            return
            
        for ability_data in world_template.abilities:
            try:
                # Create ability
                ability = Ability(
                    name=ability_data.get('name', 'Unnamed Ability'),
                    description=ability_data.get('description', ''),
                    campaign_id=campaign_id
                )
                
                self.db_manager.save_ability(ability)
                
            except Exception as e:
                print(f"Error creating ability {ability_data.get('name', 'Unnamed')}: {e}")
    
    def create_character(self, campaign_id: uuid.UUID, character_data: Dict[str, Any]) -> Character:
        """
        Create a new character in the campaign.
        
        Args:
            campaign_id: ID of the campaign
            character_data: Dictionary containing character data
            
        Returns:
            The created Character object
        """
        character = Character(
            name=character_data.get('name', 'Unnamed Character'),
            description=character_data.get('description', ''),
            campaign_id=campaign_id
        )
        
        self.db_manager.save_character(character)
        return character
    
    def create_initial_session(self, campaign_id: uuid.UUID) -> Session:
        """
        Create an initial session for the campaign.
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            The created Session object
        """
        session = Session(
            name="Initial Session",
            description="Session created at campaign start",
            campaign_id=campaign_id
        )
        
        self.db_manager.save_session(session)
        return session


# Convenience function for initialization
def initialize_campaign_from_world_template(
    db_manager,
    world_template: WorldModel, 
    campaign_name: str,
    campaign_description: str = "",
    player_character_data: Optional[Dict[str, Any]] = None
) -> uuid.UUID:
    """
    Convenience function to initialize a campaign from a world template.
    
    Args:
        db_manager: DatabaseManager instance
        world_template: The WorldModel template 
        campaign_name: Name for the new campaign
        campaign_description: Description of the campaign
        player_character_data: Data for creating the player character
        
    Returns:
        UUID of the created campaign
    """
    initializer = CampaignInitializer(db_manager)
    return initializer.initialize_campaign_from_world(
        world_template,
        campaign_name,
        campaign_description,
        player_character_data
    )