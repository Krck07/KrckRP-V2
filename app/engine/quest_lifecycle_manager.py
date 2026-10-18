"""
Quest Lifecycle Manager for KrckRP engine.
Manages quest state transitions based on validated Extractor events.
Handles proposed -> active -> completed/failed lifecycle.
"""

from typing import Dict, Any, List, Optional
import logging
import uuid
from datetime import datetime

# Import database models
from app.models.database_models import DatabaseManager, Quest

logger = logging.getLogger(__name__)

class QuestLifecycleManager:
    """
    Manages the complete lifecycle of quests in KrckRP.
    
    Quest States:
    - Proposed: New quest identified but not yet active
    - Active: Quest is currently being pursued 
    - Completed: Quest has been successfully finished
    - Failed: Quest has failed or been abandoned
    
    Transitions are triggered by Extractor events that contain quest-related information.
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the quest lifecycle manager."""
        self.db_manager = db_manager or DatabaseManager()
        
    async def handle_extractor_events(self, turn_data: Dict[str, Any], extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process events from the Extractor that affect quests.
        
        This method listens to validated Extractor events and transitions quest states
        based on the information in those events.
        
        Args:
            turn_data (Dict): Original turn data
            extraction_result (Dict): Result from data extraction
            
        Returns:
            Dict: Updated extraction result with any modifications to quest state
        """
        try:
            # Process quest-related events from extraction
            updated_extraction = extraction_result.copy()
            
            # Check for new quests proposed by the extractor
            if 'proposed_quests' in extraction_result:
                await self._handle_proposed_quests(extraction_result['proposed_quests'], turn_data)
                
            # Check for quest state changes  
            if 'quest_updates' in extraction_result:
                updated_extraction['quest_updates'] = await self._process_quest_updates(
                    extraction_result['quest_updates']
                )
            
            # Check for completed/failed quests
            if 'completed_quests' in extraction_result:
                await self._handle_completed_quests(extraction_result['completed_quests'])
                
            if 'failed_quests' in extraction_result:
                await self._handle_failed_quests(extraction_result['failed_quests'])
            
            return updated_extraction
            
        except Exception as e:
            logger.error(f"Error handling extractor events for quests: {e}")
            # Return original result on error to avoid breaking the pipeline
            return extraction_result
    
    async def _handle_proposed_quests(self, proposed_quests: List[Dict[str, Any]], turn_data: Dict[str, Any]) -> None:
        """
        Handle newly proposed quests from the Extractor.
        
        Args:
            proposed_quests (List): List of new quest proposals
            turn_data (Dict): Original turn data containing campaign info
        """
        try:
            for proposal in proposed_quests:
                # Create a new quest with "proposed" status or similar initial state
                quest_data = {
                    'name': proposal.get('title', 'Unnamed Quest'),
                    'description': proposal.get('summary', ''),
                    'campaign_id': uuid.UUID(turn_data['campaign_id']) if isinstance(turn_data['campaign_id'], str) else turn_data['campaign_id']
                }
                
                # Add the new quest to database
                await self._create_quest(quest_data)
                
        except Exception as e:
            logger.error(f"Error handling proposed quests: {e}")
            
    async def _process_quest_updates(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process quest state updates from the Extractor.
        
        Args:
            updates (List): List of quest update events
            
        Returns:
            List: Updated list with any modifications
        """
        updated_list = []
        try:
            for update in updates:
                quest_id = uuid.UUID(update['quest_id']) if isinstance(update['quest_id'], str) else update['quest_id']
                
                # Determine what state change to apply based on the update content  
                if 'status' in update:
                    await self._update_quest_status(quest_id, update['status'])
                    
                updated_list.append(update)
            
        except Exception as e:
            logger.error(f"Error processing quest updates: {e}")
            
        return updated_list
    
    async def _handle_completed_quests(self, completed_quests: List[Dict[str, Any]]) -> None:
        """
        Handle quests that have been marked as completed.
        
        Args:
            completed_quests (List): List of completed quest identifiers
        """
        try:
            for completion in completed_quests:
                quest_id = uuid.UUID(completion['quest_id']) if isinstance(completion['quest_id'], str) else completion['quest_id']
                await self._update_quest_status(quest_id, 'completed')
                
        except Exception as e:
            logger.error(f"Error handling completed quests: {e}")
    
    async def _handle_failed_quests(self, failed_quests: List[Dict[str, Any]]) -> None:
        """
        Handle quests that have been marked as failed.
        
        Args:
            failed_quests (List): List of failed quest identifiers
        """
        try:
            for failure in failed_quests:
                quest_id = uuid.UUID(failure['quest_id']) if isinstance(failure['quest_id'], str) else failure['quest_id']
                await self._update_quest_status(quest_id, 'failed')
                
        except Exception as e:
            logger.error(f"Error handling failed quests: {e}")
    
    async def _create_quest(self, quest_data: Dict[str, Any]) -> None:
        """
        Create a new quest in the database.
        
        Args:
            quest_data (Dict): Quest data to create
        """
        try:
            # In a real implementation this would use the DatabaseManager directly
            logger.info(f"Creating new quest: {quest_data['name']}")
            
        except Exception as e:
            logger.error(f"Error creating quest: {e}")
    
    async def _update_quest_status(self, quest_id: uuid.UUID, status: str) -> None:
        """
        Update the status of an existing quest.
        
        Args:
            quest_id (uuid.UUID): ID of the quest to update
            status (str): New status for the quest
        """
        try:
            # In a real implementation this would query and update the database
            
            logger.info(f"Updating quest {quest_id} status to: {status}")
            
        except Exception as e:
            logger.error(f"Error updating quest status: {e}")

    async def get_quest_state(self, campaign_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get current state of all quests for a campaign.
        
        Args:
            campaign_id (uuid.UUID): The campaign to query
            
        Returns:
            Dict: Quest states information
        """
        try:
            # This would fetch the current quest status from DB
            return {
                "status": "success",
                "quests": []
            }
        except Exception as e:
            logger.error(f"Error getting quest state: {e}")
            return {"status": "error", "quests": []}