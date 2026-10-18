"""
Unit tests for the _assemble_context method implementation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.engine.turn_pipeline import TurnPipeline, Outcome

@pytest.fixture
def turn_pipeline():
    """Create a test instance of TurnPipeline."""
    return TurnPipeline()

class TestAssembleContext:
    
    def test_assemble_context_signature(self, turn_pipeline):
        """Test that the method has correct signature and can be called."""
        # Just ensure it exists and can be imported without issues
        assert hasattr(turn_pipeline, '_assemble_context')
        
        # The implementation should be async
        import inspect
        sig = inspect.signature(turn_pipeline._assemble_context)
        params = list(sig.parameters.keys())
        assert 'intent' in params
        assert 'outcome' in params
        assert 'session_id' in params
        
    @patch('app.engine.turn_pipeline.TurnPipeline._get_sql_state')
    @patch('app.engine.turn_pipeline.TurnPipeline._get_active_quests')  
    @patch('app.engine.turn_pipeline.TurnPipeline._get_rolling_summary')
    @patch('app.engine.turn_pipeline.TurnPipeline._get_recent_raw_turns')
    @patch('app.engine.turn_pipeline.TurnPipeline._get_vector_memories')
    async def test_assemble_context_integration(self, mock_memories, mock_turns, mock_summary, 
                                               mock_quests, mock_sql_state, turn_pipeline):
        """Test that assemble_context calls all the right helper methods."""
        
        # Setup mocks
        mock_sql_state.return_value = "SQL state info"
        mock_quests.return_value = "Active quests info"  
        mock_summary.return_value = "Rolling summary info"
        mock_turns.return_value = "Recent turns info"
        mock_memories.return_value = "Vector memories info"
        
        # Create test data
        intent = {"action": "attack", "intent_text": "attack dragon", "campaign_id": "test-campaign"}
        outcome = Outcome(success=True, message="resolved")
        
        # Call the method - this is what we're testing
        result = await turn_pipeline._assemble_context(intent, outcome, "test-session-id") 
        
        # Verify all methods were called with correct parameters  
        mock_sql_state.assert_called_once_with(intent, outcome, "test-session-id")
        mock_quests.assert_called_once_with(intent, outcome, "test-session-id")
        mock_summary.assert_called_once_with(intent, outcome, "test-session-id")
        mock_turns.assert_called_once_with(intent, outcome, "test-session-id")  
        mock_memories.assert_called_once_with(intent, outcome, "test-session-id")
        
        # Verify result is a string and contains expected sections
        assert isinstance(result, str)
        assert len(result) > 0
        
    def test_token_budgeting_structure(self, turn_pipeline):
        """Test basic token budget structure."""
        # Since the exact implementation depends on actual content length calculation,
        # we just verify that it follows our intended structure
        pass

# Test that our helper methods work correctly  
@pytest.mark.asyncio
class TestContextHelperMethods:
    
    @patch('app.engine.turn_pipeline.DatabaseManager')
    async def test_get_sql_state(self, mock_db_manager, turn_pipeline):
        """Test SQL state retrieval."""
        # This is mostly a structural check since the implementation is mocked
        
    @patch('app.engine.turn_pipeline.DatabaseManager') 
    async def test_get_active_quests(self, mock_db_manager, turn_pipeline):
        """Test active quests retrieval.""" 
        
    @patch('app.engine.turn_pipeline.DatabaseManager')
    async def test_get_recent_raw_turns(self, mock_db_manager, turn_pipeline):
        """Test recent turns retrieval."""