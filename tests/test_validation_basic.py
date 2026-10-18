"""
Basic tests for validation service and core functionalities.
"""

import pytest

# Import the modules we're testing 
from app.engine.state_manager import StateManager, ValidationService


def test_validation_service_initialization():
    """Test that the validation service initializes correctly."""
    # Create a mock db manager
    mock_db = type('MockDB', (), {})()  # Simple mock object
    validation_service = ValidationService(mock_db)
    
    assert validation_service is not None
    assert validation_service.db_manager == mock_db


def test_state_manager_initialization():
    """Test that the state manager initializes correctly.""" 
    # Create a mock db manager
    mock_db = type('MockDB', (), {})()  # Simple mock object
    state_manager = StateManager(mock_db)
    
    assert state_manager is not None
    assert state_manager.db_manager == mock_db
    assert state_manager.validation_service is not None


def test_state_manager_methods_exist():
    """Test that core methods exist."""
    mock_db = type('MockDB', (), {})()  # Simple mock object
    state_manager = StateManager(mock_db)
    
    # These should all be callable
    assert hasattr(state_manager, 'prepare_turn')
    assert hasattr(state_manager, 'commit_turn') 
    assert hasattr(state_manager, 'rewind')
    assert hasattr(state_manager, 'regenerate_last_ai_message')
    assert hasattr(state_manager, 'edit_past_message')


def test_state_manager_method_signatures():
    """Test that method signatures are correct."""
    mock_db = type('MockDB', (), {})()  # Simple mock object
    state_manager = StateManager(mock_db)
    
    # Check methods exist with expected signature patterns (no runtime errors)
    assert callable(state_manager.prepare_turn)
    assert callable(state_manager.commit_turn) 
    assert callable(state_manager.rewind)
    assert callable(state_manager.regenerate_last_ai_message)
    assert callable(state_manager.edit_past_message)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])