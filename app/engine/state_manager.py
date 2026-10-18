"""
State Manager for KrckRP engine.
Handles game state management, turn processing, and database commits.
"""

from typing import Dict, Any, Optional
import asyncio
import logging
from datetime import datetime

# Import database models
from app.models.database_models import GameTurn, GameState, DatabaseManager

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages game state for KrckRP including turn processing and database operations.
    
    Ensures that state changes are only committed after successful narrative generation 
    and data extraction to maintain consistency.
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the state manager."""
        self.db_manager = db_manager or DatabaseManager()
        
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
            # Create a new game turn record
            game_turn = GameTurn(
                turn_id=turn_data["turn_id"],
                timestamp=datetime.fromisoformat(turn_data["timestamp"]),
                prompt=turn_data["prompt"],
                narrative=extraction_result.get("original_narrative", ""),
                extraction_data=json.dumps(extraction_result),
                status="completed"
            )
            
            # Save to database
            await self.db_manager.save_turn(game_turn)
            
            # Update game state if needed (this would depend on your specific implementation)
            result = {
                "turn_id": turn_data["turn_id"],
                "status": "committed",
                "extraction_result": extraction_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Turn committed successfully: {turn_data['turn_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Error committing turn: {e}")
            raise RuntimeError(f"Failed to commit turn: {e}")

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

# For backward compatibility with existing code that might expect this class to be directly accessible
state_manager = StateManager()