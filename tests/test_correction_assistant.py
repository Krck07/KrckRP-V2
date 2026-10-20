"""
Tests for the Correction Assistant and EventLog functionality.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import UUID, uuid4
from datetime import datetime

# Import the modules we're testing
from app.engine.correction_assistant import CorrectionAssistant
from app.models.database_models import DatabaseManager, EventLog


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager for testing."""
    db_manager = Mock(spec=DatabaseManager)
    
    # Set up default responses
    character_id = uuid4()
    location_id = uuid4()
    item_id = uuid4() 
    quest_id = uuid4()
    
    # Mock get_character and related methods
    db_manager.get_character.return_value = Mock(
        id=character_id,
        name="Test Character",
        location_id=None
    )
    
    db_manager.get_location.return_value = Mock(
        id=location_id, 
        name="Test Location"
    )
    
    db_manager.get_item.return_value = Mock(
        id=item_id,
        name="Test Item"
    )
    
    db_manager.get_quest.return_value = Mock(
        id=quest_id,
        name="Test Quest",
        status="active",
        progress=0
    )
    
    # Mock update methods (they don't return anything)
    db_manager.update_character_location = Mock()
    db_manager.update_character_stat = Mock() 
    db_manager.update_quest = Mock()
    
    # Mock log_event method to capture the EventLog entry
    db_manager.log_event = Mock()
    
    return db_manager


@pytest.fixture
def correction_assistant(mock_db_manager):
    """Create a CorrectionAssistant instance with mock dependencies."""
    assistant = CorrectionAssistant(db_manager=mock_db_manager)
    return assistant


class TestCorrectionAssistant:
    
    @pytest.mark.asyncio
    async def test_move_character_creates_event_log(self, correction_assistant, mock_db_manager):
        """Test that move_character creates an EventLog entry with correct source."""
        character_id = uuid4()
        location_id = uuid4()
        
        # Mock the database responses 
        mock_character = Mock(id=character_id, name="Test Character", location_id=None)
        mock_location = Mock(id=location_id, name="Test Location")
        
        mock_db_manager.get_character.return_value = mock_character
        mock_db_manager.get_location.return_value = mock_location
        
        # Execute the move_character method 
        result = await correction_assistant.move_character(character_id, location_id)
        
        # Verify successful execution
        assert result["success"] is True
        
        # Verify that log_event was called with correct parameters
        assert mock_db_manager.log_event.called
        
        # Get the event that was logged
        call_args = mock_db_manager.log_event.call_args[0][0]  # First argument of first call
        
        # Check that it's an EventLog entry with source="assistant_correction"
        assert isinstance(call_args, EventLog)
        assert call_args.entity_type == "Character"
        assert call_args.field == "location_id" 
        assert call_args.operation == "UPDATE"
        assert call_args.witness_metadata == "assistant_correction"


    @pytest.mark.asyncio
    async def test_set_stat_creates_event_log(self, correction_assistant, mock_db_manager):
        """Test that set_stat creates an EventLog entry with correct source."""
        character_id = uuid4()
        
        # Mock the database responses 
        mock_character = Mock(id=character_id, name="Test Character", strength=10)
        mock_db_manager.get_character.return_value = mock_character
        
        # Execute the set_stat method
        result = await correction_assistant.set_stat(character_id, "strength", 15)
        
        # Verify successful execution
        assert result["success"] is True
        
        # Verify that log_event was called with correct parameters 
        assert mock_db_manager.log_event.called
        
        # Get the event that was logged
        call_args = mock_db_manager.log_event.call_args[0][0]  # First argument of first call
        
        # Check that it's an EventLog entry with source="assistant_correction"
        assert isinstance(call_args, EventLog)
        assert call_args.entity_type == "Character" 
        assert call_args.field == "strength"
        assert call_args.operation == "UPDATE"
        assert call_args.witness_metadata == "assistant_correction"


    @pytest.mark.asyncio
    async def test_update_quest_creates_event_log(self, correction_assistant, mock_db_manager):
        """Test that update_quest creates EventLog entries with correct source."""
        quest_id = uuid4()
        
        # Mock the database responses 
        mock_quest = Mock(id=quest_id, name="Test Quest", status="active", progress=0)
        mock_db_manager.get_quest.return_value = mock_quest
        
        # Execute the update_quest method
        result = await correction_assistant.update_quest(quest_id, status="completed")
        
        # Verify successful execution
        assert result["success"] is True
        
        # Verify that log_event was called (at least once)
        assert mock_db_manager.log_event.called
        
        # Get all events that were logged
        call_args_list = [call[0][0] for call in mock_db_manager.log_event.call_args_list]
        
        # Check that at least one event is an EventLog entry with source="assistant_correction"
        event_logs = [arg for arg in call_args_list if isinstance(arg, EventLog)]
        assert len(event_logs) >= 1
        
        # Verify the event has correct metadata
        event_log = event_logs[0]
        assert event_log.entity_type == "Quest" 
        assert event_log.field == "status"
        assert event_log.operation == "UPDATE"
        assert event_log.witness_metadata == "assistant_correction"


    @pytest.mark.asyncio
    async def test_give_item_creates_event_log(self, correction_assistant, mock_db_manager):
        """Test that give_item creates an EventLog entry with correct source."""
        character_id = uuid4()
        item_id = uuid4() 
        
        # Mock the database responses 
        mock_character = Mock(id=character_id, name="Test Character")
        mock_item = Mock(id=item_id, name="Test Item") 
        mock_db_manager.get_character.return_value = mock_character
        mock_db_manager.get_item.return_value = mock_item
        
        # Execute the give_item method
        result = await correction_assistant.give_item(character_id, item_id)
        
        # Verify successful execution
        assert result["success"] is True
        
        # Verify that log_event was called with correct parameters 
        assert mock_db_manager.log_event.called
        
        # Get the event that was logged
        call_args = mock_db_manager.log_event.call_args[0][0]  # First argument of first call
        
        # Check that it's an EventLog entry with source="assistant_correction"
        assert isinstance(call_args, EventLog)
        assert call_args.entity_type == "Character"
        assert call_args.field == "inventory"
        assert call_args.operation == "UPDATE"  
        assert call_args.witness_metadata == "assistant_correction"


    @pytest.mark.asyncio
    async def test_available_tools(self, correction_assistant):
        """Test that the assistant returns correct list of available tools."""
        tools = await correction_assistant.get_available_tools()
        
        expected_tools = ["move_character", "set_stat", "give_item", "update_quest"]
        assert set(tools) == set(expected_tools)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])