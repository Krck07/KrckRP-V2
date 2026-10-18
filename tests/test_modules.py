"""
Tests for individual KrckRP modules.
"""

import pytest
from app.llm.kobold_cpp_client import KoboldCppClient
from app.llm.extractor import Extractor
from app.engine.state_manager import StateManager

def test_kobold_cpp_client_initialization():
    """Test that KoboldCpp client can be initialized."""
    client = KoboldCppClient()
    assert client is not None

def test_extractor_initialization():
    """Test that extractor can be initialized."""
    extractor = Extractor()
    assert extractor is not None
    
def test_state_manager_initialization():
    """Test that state manager can be initialized."""
    state_manager = StateManager()
    assert state_manager is not None

def test_extract_schema_selection():
    """Test schema selection in extractor."""
    extractor = Extractor()
    
    # Test with default turn data
    turn_data = {"prompt": "test"}
    schema_name = extractor._get_extraction_schema(turn_data)
    assert schema_name == "game_state"
    
if __name__ == "__main__":
    pytest.main([__file__])