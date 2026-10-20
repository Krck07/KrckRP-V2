"""
Integration tests for the full World Creation flow including Form Editor, Campaign Initializer.
"""

import pytest
from unittest.mock import Mock

# We'll test that we have the necessary components in place
# These are more integration-style tests


def test_form_editor_components_exist():
    """Test that required form editor components exist."""
    # This is a placeholder - actual component testing would happen in frontend tests
    
    # Check that we have the right files created
    import os
    
    assert os.path.exists('app/static/js/form_editor.js')
    assert os.path.exists('app/static/world_form.html')


def test_character_creator_components_exist():
    """Test that required character creator components exist."""
    # This is a placeholder - actual component testing would happen in frontend tests
    
    # Check that we have the right files created
    import os
    
    assert os.path.exists('app/static/js/character_creator.js')
    assert os.path.exists('app/static/character_creator.html')


def test_campaign_initializer_components_exist():
    """Test that campaign initializer components exist."""
    # Check that we have the right file created  
    import os
    
    assert os.path.exists('app/engine/campaign_initializer.py')


def test_world_models_integration():
    """Test that world models are correctly structured for initialization."""
    
    from app.models.world_models import World, WORLD_SCHEMA
    
    # Test that basic world creation works
    world = World(
        name="Integration Test",
        description="A world for integration testing"
    )
    
    assert world.name == "Integration Test"
    assert world.description == "A world for integration testing" 
    
    # Test dict conversion
    world_dict = world.to_dict()
    assert isinstance(world_dict, dict)
    assert world_dict["name"] == "Integration Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])