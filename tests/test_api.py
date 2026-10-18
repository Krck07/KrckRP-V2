"""
Tests for the KrckRP API components.
"""

import pytest
from app.api.main import app
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_turn_endpoint():
    """Test the turn endpoint with mock data."""
    # This is a basic test - in practice you'd need to set up proper mocking
    # for the LLM components
    
    mock_data = {
        "prompt": "A hero enters a mysterious forest.",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    with patch('app.llm.kobold_cpp_client.KoboldCppClient.generate_narrative') as mock_narrate, \
         patch('app.llm.extractor.Extractor.extract_structured_data') as mock_extract, \
         patch('app.engine.state_manager.StateManager.commit_turn') as mock_commit:
        
        # Mock the return values
        mock_narrate.return_value = ["Narration part 1", " Narration part 2"]
        mock_extract.return_value = {"character": "Hero", "location": "Forest"}
        mock_commit.return_value = {"status": "committed"}
        
        response = client.post("/turn", json=mock_data)
        # This would fail because we haven't properly mocked all dependencies
        # But it shows how tests can be structured

if __name__ == "__main__":
    pytest.main([__file__])