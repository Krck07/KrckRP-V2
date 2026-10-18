"""
Summarizer module for KrckRP engine.
This module handles compression of older raw turns into a narrative summary,
which is stored in the Summary table for efficient history management.
"""

from typing import List, Optional
import asyncio
import logging
from datetime import datetime
from uuid import UUID

# Import database models and managers
from app.models.database_models import GameTurn, Summary, DatabaseManager, Session

logger = logging.getLogger(__name__)


class Summarizer:
    """
    A module that compresses older raw turns into narrative summaries.
    
    The summarizer processes game turns that are beyond a certain threshold,
    condensing their content into high-level narratives to save context tokens
    and improve performance for long-running games.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the Summarizer with database manager.
        
        Args:
            db_manager (DatabaseManager): The database manager instance
        """
        self.db_manager = db_manager

    async def compress_turns(self, campaign_id: UUID, max_turns_to_compress: int = 10) -> Optional[UUID]:
        """
        Compress a set of older turns into a narrative summary.
        
        Args:
            campaign_id (UUID): The campaign ID to process
            max_turns_to_compress (int): Maximum number of turns to compress
            
        Returns:
            UUID: The ID of the created summary, or None if no compression was needed
        """
        try:
            # Get recent game turns for this campaign that need summarization
            recent_turns = await self._get_recent_turns(campaign_id, max_turns_to_compress)
            
            if not recent_turns or len(recent_turns) < 2:
                logger.debug("Not enough turns to compress")
                return None
            
            # Create summary content from the turns  
            summary_content = await self._create_summary_text(recent_turns)
            
            # Save the summary to database
            summary_id = await self._save_summary(campaign_id, summary_content)
            
            logger.info(f"Successfully compressed {len(recent_turns)} turns into summary with ID: {summary_id}")
            return summary_id
            
        except Exception as e:
            logger.error(f"Error during turn compression: {str(e)}")
            raise

    async def _get_recent_turns(self, campaign_id: UUID, max_count: int) -> List[GameTurn]:
        """
        Retrieve recent game turns for a campaign.
        
        Args:
            campaign_id (UUID): The campaign ID to query
            max_count (int): Maximum number of turns to retrieve
            
        Returns:
            List[GameTurn]: A list of GameTurn objects ordered by turn_id ascending
        """
        return await self.db_manager.get_recent_turns(campaign_id, max_count)

    async def _create_summary_text(self, turns: List[GameTurn]) -> str:
        """
        Create a narrative summary from multiple game turns.
        
        Args:
            turns (List[GameTurn]): The list of GameTurn objects to summarize
            
        Returns:
            str: A narrative summary of the turns
        """
        # For now we'll create a simple text-based summary
        # In a real implementation, this would use an LLM to generate natural summaries
        
        summary_lines = []
        
        for turn in turns:
            if turn.narrative and len(turn.narrative) > 0:
                # Extract key elements from the narrative 
                summary_lines.append(f"Turn {turn.turn_id}: {self._extract_key_elements(turn.narrative)}")
                
        return "\n".join(summary_lines)

    def _extract_key_elements(self, narrative: str) -> str:
        """
        Extract key elements from a narrative for summarization.
        
        Args:
            narrative (str): The full narrative text
            
        Returns:
            str: Key elements extracted
        """
        # For now we return the first 100 characters as a placeholder
        # In practice, this would be more sophisticated
        
        if len(narrative) > 100:
            return narrative[:100] + "..."
        else:
            return narrative

    async def _save_summary(self, campaign_id: UUID, content: str) -> UUID:
        """
        Save a summary to the database.
        
        Args:
            campaign_id (UUID): The campaign ID to link this summary to
            content (str): The summary text
            
        Returns:
            UUID: The ID of the created summary
        """
        # Create new Summary instance
        summary = Summary(
            content=content,
            campaign_id=campaign_id,
            created_at=datetime.utcnow()
        )
        
        with Session(self.db_manager.engine) as session:
            session.add(summary)
            session.commit()
            session.refresh(summary)
            
        return summary.id

    async def get_summary(self, summary_id: UUID) -> Optional[Summary]:
        """
        Retrieve a specific summary from the database.
        
        Args:
            summary_id (UUID): The ID of the summary to retrieve
            
        Returns:
            Summary or None if not found
        """
        with Session(self.db_manager.engine) as session:
            return session.query(Summary).filter(Summary.id == summary_id).first()