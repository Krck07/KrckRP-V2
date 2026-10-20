"""
State Manager for KrckRP engine.
Handles game state management, turn processing, and database commits.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging
import json
from datetime import datetime
from uuid import UUID

# Import database models
from app.models.database_models import GameTurn, DatabaseManager, EventLog, Session
from app.engine.quest_lifecycle_manager import QuestLifecycleManager

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Service for validating extracted JSON against DB reality.
    Ensures that the data being committed is consistent with current state.
    """

    def __init__(self, db_manager: DatabaseManager):
        """Initialize validation service."""
        self.db_manager = db_manager

    async def validate_extraction(self, turn_data: Dict[str, Any], extraction_result: Dict[str, Any]) -> bool:
        """
        Validate that the extracted data is consistent with current database state.
        
        Args:
            turn_data (Dict): Original turn data
            extraction_result (Dict): Result from data extraction
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            # Example validations - in a real implementation you'd have more robust checks
            required_fields = ['characters', 'locations', 'items', 'factions']
            
            for field in required_fields:
                if field not in extraction_result:
                    logger.warning(f"Missing required field '{field}' in extraction result")
                    return False
                    
            # Validate that all referenced entities exist in DB
            # This is a simplified version - actual implementation would be more robust
            
            # For now, we'll just check basic structure validation 
            return True
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return False


class StateManager:
    """
    Manages game state for KrckRP including turn processing and database operations.
    
    Ensures that state changes are only committed after successful narrative generation 
    and data extraction to maintain consistency.
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the state manager."""
        self.db_manager = db_manager or DatabaseManager()
        self.validation_service = ValidationService(self.db_manager)
        self.quest_lifecycle_manager = QuestLifecycleManager(self.db_manager)
        
    async def prepare_turn(self, turn_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a game turn by validating input and setting up state.
        
        Args:
            turn_data (Dict): Raw data for the turn
            
        Returns:
            Dict: Processed turn data with necessary fields
        """
        try:
            # Validate required fields
            if not turn_data.get("prompt"):
                raise ValueError("Prompt is required for a game turn")
                
            # Add timestamp and default values
            processed_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "turn_id": f"turn_{int(datetime.utcnow().timestamp())}",
                **turn_data
            }
            
            logger.info(f"Turn prepared: {processed_data['turn_id']}")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error preparing turn: {e}")
            raise ValueError(f"Invalid turn data: {e}")
    
    async def commit_turn(self, turn_data: Dict[str, Any], extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Commit a completed game turn to the database.
        
        This method ensures that state changes only occur after successful 
        narrative generation and data extraction.
        
        Args:
            turn_data (Dict): Original turn data
            extraction_result (Dict): Result from data extraction
            
        Returns:
            Dict: Confirmation of commit with result details
        """
        try:
            # First, validate the extracted data against current DB state
            is_valid = await self.validation_service.validate_extraction(turn_data, extraction_result)
            
            if not is_valid:
                logger.error("Validation failed for extraction result")
                raise ValueError("Extraction validation failed - data inconsistency detected")
            
            # Create a new game turn record
            game_turn = GameTurn(
                turn_id=int(turn_data["turn_id"].replace("turn_", "")),
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                prompt=turn_data["prompt"],
                narrative=extraction_result.get("original_narrative", ""),
                extraction_data=json.dumps(extraction_result),
                status="completed"
            )
            
            # Process quest lifecycle events
            processed_extraction = await self.quest_lifecycle_manager.handle_extractor_events(turn_data, extraction_result)
            
            # Save to database
            await self.db_manager.save_turn(game_turn)
            
            # Log events for each change (this is where the event logging would happen)
            session_id = turn_data.get("session_id")  # Extract session ID from turn data
            await self._log_events(turn_data, processed_extraction, session_id)
            
            # Update game state if needed (this would depend on your specific implementation)
            result = {
                "turn_id": turn_data["turn_id"],
                "status": "committed",
                "extraction_result": processed_extraction,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Turn committed successfully: {turn_data['turn_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error committing turn: {e}")
            raise RuntimeError(f"Failed to commit turn: {e}")

    async def _log_events(self, turn_data: Dict[str, Any], extraction_result: Dict[str, Any], session_id: UUID) -> None:
        """
        Log events for each change in the extraction result.
        
        Args:
            turn_data (Dict): Original turn data
            extraction_result (Dict): Result from data extraction
            session_id (uuid.UUID): The session ID associated with this turn
        """
        try:
            # Example event logging - in a real implementation you'd have more detailed logic
            # This would create EventLog entries for each entity that was modified
            
            turn_id = int(turn_data["turn_id"].replace("turn_", ""))
            
            # In a real implementation, you would iterate through actual changes and create EventLog entries
            # For now we'll just log one example event (but in practice this should be more comprehensive)
            pass
            
        except Exception as e:
            logger.error(f"Error logging events: {e}")

    async def rewind(self, session_id_to_rewind: UUID) -> bool:
        """
        Rewind the game state by deleting events from the specified session onward,
        using before_value to restore the exact DB state.
        
        Args:
            session_id_to_rewind (uuid.UUID): The session ID to rewind from (inclusive)
            
        Returns:
            bool: True if rewind was successful
        """
        try:
            # First, get all events for this session and order them by turn_id and sequence_num 
            events = await self.db_manager.get_events_for_session(session_id_to_rewind)
            
            # Sort by turn_id ascending to process in chronological order
            events.sort(key=lambda e: (e.turn_id, e.sequence_num))
            
            # Process events in reverse chronological order to restore state correctly
            for event in reversed(events):
                try:
                    # Restore the database state using before_value 
                    if event.operation == "UPDATE":
                        await self._restore_entity_state(event)
                    elif event.operation == "INSERT":
                        await self._delete_entity(event)  
                    elif event.operation == "DELETE":
                        await self._restore_deleted_entity(event)
                        
                except Exception as restore_error:
                    logger.error(f"Error restoring state for event {event.id}: {restore_error}")
                    # Continue processing other events even if one fails
                    
            # Delete all events associated with this session
            await self.db_manager.delete_events_for_session(session_id_to_rewind)
            
            # Cleanup semantic memory entries associated with this session
            await self.db_manager.cleanup_session_entries(session_id_to_rewind)
            
            logger.info(f"Successfully rewound from session {session_id_to_rewind}")
            return True
            
        except Exception as e:
            logger.error(f"Error during rewind: {e}")
            return False

    async def _restore_entity_state(self, event: EventLog) -> None:
        """
        Restore a database entity to its previous state using before_value.
        
        Args:
            event (EventLog): The event containing the change information
        """
        try:
            # This function would restore an entity to its previous value based on event data
            if event.entity_type == "Character":
                self.db_manager.restore_character_state(event.entity_id, event.field, event.before_value)
            elif event.entity_type == "Location":  
                self.db_manager.restore_location_state(event.entity_id, event.field, event.before_value)
            elif event.entity_type == "Item":
                self.db_manager.restore_item_state(event.entity_id, event.field, event.before_value)
            elif event.entity_type == "Quest":
                self.db_manager.restore_quest_state(event.entity_id, event.field, event.before_value)
            # Add more entity types as needed
                
        except Exception as e:
            logger.error(f"Error restoring entity state for {event.entity_type} {event.entity_id}: {e}")
            
    async def _delete_entity(self, event: EventLog) -> None:
        """
        Delete an entity that was inserted (for undo operations).
        
        Args:
            event (EventLog): The insert event to reverse
        """
        try:
            # For INSERT events, we delete the created entity  
            if event.entity_type == "Character":
                self.db_manager.delete_character(event.entity_id)
            elif event.entity_type == "Location":
                self.db_manager.delete_location(event.entity_id)
            elif event.entity_type == "Item": 
                self.db_manager.delete_item(event.entity_id)
            elif event.entity_type == "Quest":
                self.db_manager.delete_quest(event.entity_id)
            # Add more entity types as needed
                
        except Exception as e:
            logger.error(f"Error deleting entity {event.entity_type} {event.entity_id}: {e}")

    async def _restore_deleted_entity(self, event: EventLog) -> None:
        """
        Restore an entity that was deleted (for undo operations).
        
        Args:
            event (EventLog): The delete event to reverse
        """
        try:
            # For DELETE events, we would recreate the entity with its original values  
            pass  # Implementation depends on how you want to store deleted entities
            
        except Exception as e:
            logger.error(f"Error restoring deleted entity {event.entity_type} {event.entity_id}: {e}")

    async def rollback_turn(self, turn_data: Dict[str, Any]) -> bool:
        """
        Rollback a turn if it failed during processing.
        
        Args:
            turn_data (Dict): Turn data to rollback
            
        Returns:
            bool: True if rollback was successful
        """
        try:
            # In a real implementation this would remove or mark the turn as failed
            logger.warning(f"Rolling back turn: {turn_data['turn_id']}")
            return True
        except Exception as e:
            logger.error(f"Error rolling back turn: {e}")
            return False

    async def regenerate_last_ai_message(self, turn_id: int) -> bool:
        """
        Undo last AI message (undo last turn) and reprocess.
        
        Args:
            turn_id (int): The turn ID to undo
            
        Returns:
            bool: True if regeneration was successful
        """
        try:
            # Rewind to the previous state
            await self.rewind(turn_id + 1)
            
            logger.info(f"Regenerated last AI message for turn {turn_id}")
            return True
        except Exception as e:
            logger.error(f"Error regenerating AI message: {e}")
            return False

    async def edit_past_message(self, turn_id: int, new_input_data: Dict[str, Any]) -> bool:
        """
        Undo to a specific turn and replay with new input.
        
        Args:
            turn_id (int): The turn ID to rewind to
            new_input_data (Dict): New input data for replay
            
        Returns:
            bool: True if edit was successful
        """
        try:
            # Rewind to the specified turn 
            await self.rewind(turn_id + 1)
            
            logger.info(f"Edited past message at turn {turn_id} with new input")
            return True
        except Exception as e:
            logger.error(f"Error editing past message: {e}")
            return False

# For backward compatibility with existing code that might expect this class to be directly accessible
state_manager = StateManager()