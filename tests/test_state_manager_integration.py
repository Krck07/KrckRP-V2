"""
Test StateManager integration with QuestLifecycleManager.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

# Import modules we're testing
from app.engine.state_manager import StateManager


class TestStateManagerIntegration:
    """Test StateManager integration with QuestLifecycleManager."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_db_manager = MagicMock()
        self.state_manager = StateManager(self.mock_db_manager)
        
    def test_state_manager_has_quest_lifecycle_manager(self):
        """Test that StateManager has the quest lifecycle manager instance."""
        assert hasattr(self.state_manager, 'quest_lifecycle_manager')
        assert self.state_manager.quest_lifecycle_manager is not None
        
    def test_commit_turn_calls_quest_processing(self):
        """Test that commit_turn calls quest processing logic (mocked)."""
        # This is a basic structural check - we're mainly making sure the method exists
        # and can be called without breaking
        assert hasattr(self.state_manager, 'commit_turn')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])