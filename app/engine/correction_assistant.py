"""
Correction Assistant for KrckRP engine.
Provides a safe interface for correcting game state errors through a whitelist of allowed operations.
"""

from typing import Dict, Any, List, Optional
import logging
from uuid import UUID

# Import database models and managers
from app.models.database_models import DatabaseManager, Character, Location, Item, Quest, Session, EventLog
from app.engine.state_manager import StateManager

logger = logging.getLogger(__name__)

class CorrectionAssistant:
    """
    Provides a safe interface for correcting game state errors.
    
    This assistant operates with strict tool whitelisting to prevent arbitrary database modifications.
    Allowed operations include: 
    - move_character: Move character between locations
    - set_stat: Modify character stats  
    - give_item: Give items to characters
    - update_quest: Update quest status or progress
    
    No raw SQL is allowed, only the provided safe interface methods.
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the correction assistant."""
        self.db_manager = db_manager or DatabaseManager()
        self.state_manager = StateManager(self.db_manager)
        
    async def move_character(self, character_id: UUID, new_location_id: UUID) -> Dict[str, Any]:
        """
        Move a character to a new location.
        
        Args:
            character_id (UUID): ID of the character to move
            new_location_id (UUID): ID of the new location
            
        Returns:
            Dict with result status and details
        """
        try:
            # Validate that both entities exist in the database
            character = self.db_manager.get_character(character_id)
            if not character:
                return {"success": False, "error": f"Character {character_id} not found"}
            
            location = self.db_manager.get_location(new_location_id)
            if not location:
                return {"success": False, "error": f"Location {new_location_id} not found"}
                
            # Get the current state for logging
            old_location_id = character.location_id
            
            # Perform the move operation - in a real implementation this would update character's location field in DB
            self.db_manager.update_character_location(character_id, new_location_id)
            
            logger.info(f"Moving character {character_id} to location {new_location_id}")
            
            # Log the event for undo/rewind functionality
            await self._log_correction_event(
                entity_type="Character",
                entity_id=character_id,
                field="location_id",
                operation="UPDATE",
                before_value=str(old_location_id) if old_location_id else None,
                after_value=str(new_location_id)
            )
            
            return {
                "success": True,
                "message": f"Character moved from {character.name} to {location.name}",
                "character_id": str(character_id),
                "new_location_id": str(new_location_id)
            }
        except Exception as e:
            logger.error(f"Error moving character: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_stat(self, character_id: UUID, stat_name: str, new_value: int) -> Dict[str, Any]:
        """
        Set a specific stat for a character.
        
        Args:
            character_id (UUID): ID of the character
            stat_name (str): Name of the stat to modify
            new_value (int): New value for the stat
            
        Returns:
            Dict with result status and details
        """
        try:
            # Validate that character exists
            character = self.db_manager.get_character(character_id)
            if not character:
                return {"success": False, "error": f"Character {character_id} not found"}
            
            # Get current stat value for logging
            old_value = getattr(character, stat_name, None)
            
            # Update the character's stat in DB (in a real implementation)  
            self.db_manager.update_character_stat(character_id, stat_name, new_value)
            
            logger.info(f"Setting {stat_name} for character {character_id} to {new_value}")
            
            # Log the event for undo/rewind functionality
            await self._log_correction_event(
                entity_type="Character",
                entity_id=character_id,
                field=stat_name,
                operation="UPDATE",
                before_value=str(old_value) if old_value is not None else None,
                after_value=str(new_value)
            )
            
            return {
                "success": True,
                "message": f"Set {stat_name} for {character.name} to {new_value}",
                "character_id": str(character_id),
                "stat_name": stat_name,
                "new_value": new_value
            }
        except Exception as e:
            logger.error(f"Error setting character stat: {e}")
            return {"success": False, "error": str(e)}
    
    async def give_item(self, character_id: UUID, item_id: UUID) -> Dict[str, Any]:
        """
        Give an item to a character.
        
        Args:
            character_id (UUID): ID of the character receiving the item
            item_id (UUID): ID of the item to give
            
        Returns:
            Dict with result status and details
        """
        try:
            # Validate that both entities exist in the database
            character = self.db_manager.get_character(character_id)
            if not character:
                return {"success": False, "error": f"Character {character_id} not found"}
            
            item = self.db_manager.get_item(item_id)
            if not item:
                return {"success": False, "error": f"Item {item_id} not found"}
                
            # In a real implementation this would update character's inventory in DB
            # For now we'll just log and return success (mocking)  
            
            logger.info(f"Giving item {item_id} to character {character_id}")
            
            # Log the event for undo/rewind functionality 
            await self._log_correction_event(
                entity_type="Character",
                entity_id=character_id,
                field="inventory",
                operation="UPDATE",
                before_value=None,  # In a real implementation would be previous inventory state
                after_value=str(item_id)
            )
            
            return {
                "success": True,
                "message": f"Given {item.name} to {character.name}",
                "character_id": str(character_id),
                "item_id": str(item_id)
            }
        except Exception as e:
            logger.error(f"Error giving item: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_quest(self, quest_id: UUID, status: str = None, progress: int = None) -> Dict[str, Any]:
        """
        Update a quest's status or progress.
        
        Args:
            quest_id (UUID): ID of the quest to update
            status (str): New status for the quest (optional)
            progress (int): New progress value for the quest (optional)
            
        Returns:
            Dict with result status and details
        """
        try:
            # Validate that quest exists in the database
            quest = self.db_manager.get_quest(quest_id)
            if not quest:
                return {"success": False, "error": f"Quest {quest_id} not found"}
            
            # Get current values for logging
            old_status = quest.status if status else None
            old_progress = quest.progress if progress is not None else None
            
            # In a real implementation this would update the quest's status/progress in DB
            self.db_manager.update_quest(quest_id, status=status, progress=progress)
            
            logger.info(f"Updating quest {quest_id}: status={status}, progress={progress}")
            
            result = {
                "success": True,
                "message": f"Updated quest {quest.name}",
                "quest_id": str(quest_id),
            }
            
            if status:
                # Log the event for undo/rewind functionality
                await self._log_correction_event(
                    entity_type="Quest",
                    entity_id=quest_id,
                    field="status", 
                    operation="UPDATE",
                    before_value=str(old_status) if old_status is not None else None,
                    after_value=status
                )
                result["new_status"] = status
                
            if progress is not None:
                # Log the event for undo/rewind functionality  
                await self._log_correction_event(
                    entity_type="Quest",
                    entity_id=quest_id,
                    field="progress",
                    operation="UPDATE", 
                    before_value=str(old_progress) if old_progress is not None else None,
                    after_value=str(progress)
                )
                result["new_progress"] = progress
                
            return result
        except Exception as e:
            logger.error(f"Error updating quest: {e}")
            return {"success": False, "error": str(e)}

    async def get_available_tools(self) -> List[str]:
        """
        Get list of available correction tools.
        
        Returns:
            List of tool names that can be used
        """
        return ["move_character", "set_stat", "give_item", "update_quest"]
        
    async def _log_correction_event(self, entity_type: str, entity_id: UUID, field: str, operation: str,
                                  before_value: Optional[str], after_value: Optional[str]) -> None:
        """
        Log a correction event to the EventLog table.
        
        Args:
            entity_type (str): Type of entity being modified
            entity_id (UUID): ID of the entity being modified  
            field (str): Field that was changed
            operation (str): Type of operation performed
            before_value (Optional[str]): Value before change
            after_value (Optional[str]): Value after change 
        """
        try:
            # In a real implementation we'd get current session info from the context
            # For now, this is a placeholder - in actual use you would pass session_id properly
            
            # Create an EventLog entry with source="assistant_correction"
            event_log = EventLog(
                turn_id=0,  # Placeholder, will be set when committing a turn 
                session_id=None,  # Placeholder
                entity_type=entity_type,
                entity_id=entity_id,
                field=field,
                operation=operation,
                before_value=before_value,
                after_value=after_value,
                sequence_num=0,
                witness_metadata="assistant_correction"
            )
            
            await self.db_manager.log_event(event_log)
            
        except Exception as e:
            logger.error(f"Error logging correction event: {e}")


class CorrectionAssistantAPI:
    """
    API interface for the Correction Assistant.
    
    This provides a REST-like interface to access correction assistant functions,
    but with strict validation and security controls.
    """
    
    def __init__(self, assistant: CorrectionAssistant):
        """Initialize API with reference to assistant."""
        self.assistant = assistant
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a correction tool by name with provided arguments.
        
        Args:
            tool_name (str): Name of the tool to execute
            **kwargs: Arguments for the tool
            
        Returns:
            Dict with result or error information
        """
        # Validate that tool is in whitelist
        allowed_tools = await self.assistant.get_available_tools()
        if tool_name not in allowed_tools:
            return {"success": False, "error": f"Tool '{tool_name}' not allowed"}
        
        # Execute the appropriate method based on tool name
        try:
            if tool_name == "move_character":
                return await self.assistant.move_character(**kwargs)
            elif tool_name == "set_stat":
                return await self.assistant.set_stat(**kwargs)
            elif tool_name == "give_item":  
                return await self.assistant.give_item(**kwargs)
            elif tool_name == "update_quest":
                return await self.assistant.update_quest(**kwargs)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return {"success": False, "error": str(e)}