"""
Tests for Turn Pipeline orchestrator.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.engine.turn_pipeline import TurnPipeline, Outcome, json_schema_to_gbnf

@pytest.fixture
def turn_pipeline():
    """Create a test instance of TurnPipeline."""
    return TurnPipeline()

class TestTurnPipeline:
    
    def test_init(self, turn_pipeline):
        """Test that the pipeline initializes correctly."""
        assert turn_pipeline is not None
    
    def test_outcome_creation(self):
        """Test Outcome object creation."""
        outcome = Outcome(success=True, message="test", data={"key": "value"})
        assert outcome.success == True
        assert outcome.message == "test"
        assert outcome.data["key"] == "value"
    
    def test_interpret_intent_simple(self, turn_pipeline):
        """Test simple intent interpretation."""
        input_data = {"prompt": "attack dragon"}
        intent = turn_pipeline._interpret_intent(input_data)
        
        assert intent["action"] == "attack"
        assert intent["intent_text"] == "attack dragon"
    
    def test_resolve_mechanics_stub(self, turn_pipeline):
        """Test stub mechanics resolution."""
        intent = {"action": "attack", "intent_text": "attack dragon"}
        outcome = turn_pipeline._resolve_mechanics(intent)
        
        assert outcome.success == True
        assert "attack" in outcome.message
    
    async def test_assemble_context(self, turn_pipeline):
        """Test full context assembly."""
        intent = {"action": "attack", "intent_text": "attack dragon", "campaign_id": "test-campaign-id"}
        outcome = Outcome(success=True, message="resolved")
        
        # This will test the new implementation
        context_prompt = await turn_pipeline._assemble_context(intent, outcome, "test-session-id")
        assert len(context_prompt) > 0
    
    def test_prepare_entity_payload(self, turn_pipeline):
        """Test entity payload preparation."""
        input_data = {
            "characters": [
                {"id": "char_1", "name": "Alice"},
                "Bob"
            ],
            "locations": [
                {"id": "loc_1", "name": "Forest"}
            ]
        }
        
        payload = turn_pipeline._prepare_entity_payload(input_data)
        
        assert len(payload["characters"]) == 2
        assert payload["characters"][0]["id"] == "char_1"
        assert payload["characters"][0]["name"] == "Alice"
        assert payload["characters"][1]["name"] == "Bob"
        assert len(payload["locations"]) == 1
        assert payload["locations"][0]["id"] == "loc_1"

    def test_json_schema_to_gbnf(self):
        """Test JSON schema to GBNF conversion."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        gbnf = json_schema_to_gbnf(schema, "test_schema")
        assert isinstance(gbnf, str)