"""
Tests for the Summarizer module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

# Import our modules
from app.engine.summarizer import Summarizer
from app.models.database_models import GameTurn, Summary


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    mock = MagicMock()
    return mock


@pytest.fixture
def summarizer(mock_db_manager):
    """Create a Summarizer instance with mock DB manager."""
    return Summarizer(db_manager=mock_db_manager)


class TestSummarizer:
    
    def test_init(self, mock_db_manager):
        """Test that the Summarizer initializes correctly."""
        summarizer = Summarizer(db_manager=mock_db_manager)
        assert summarizer.db_manager == mock_db_manager
    
    async def test_compress_turns_no_turns(self, summarizer, mock_db_manager):
        """Test compression when there are no turns to compress."""
        # Mock the database call to return empty list
        mock_db_manager.get_recent_turns = AsyncMock(return_value=[])
        
        result = await summarizer.compress_turns(campaign_id=uuid4())
        assert result is None
    
    async def test_compress_turns_insufficient_turns(self, summarizer, mock_db_manager):
        """Test compression when there are insufficient turns."""
        # Mock the database call to return a single turn
        mock_db_manager.get_recent_turns = AsyncMock(return_value=[MagicMock()])
        
        result = await summarizer.compress_turns(campaign_id=uuid4())
        assert result is None
    
    async def test_create_summary_text(self, summarizer):
        """Test that summary text is created properly."""
        turns = [
            MagicMock(narrative="Character did something in location"),
            MagicMock(narrative="Another character took action")
        ]
        
        # This should extract key elements from narratives
        result = await summarizer._create_summary_text(turns)
        assert isinstance(result, str)
    
    async def test_extract_key_elements(self, summarizer):
        """Test that key elements are extracted properly."""
        narrative = "This is a very long narrative about what happened in the game."
        
        # Should truncate to first 100 chars
        result = summarizer._extract_key_elements(narrative)
        assert len(result) <= 103  # 100 + "..."
    
    async def test_extract_key_elements_short(self, summarizer):
        """Test that short narratives are handled properly."""
        narrative = "Short narrative"
        
        result = summarizer._extract_key_elements(narrative)
        assert result == narrative