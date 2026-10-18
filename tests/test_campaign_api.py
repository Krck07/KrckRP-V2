"""
Tests for campaign-related API endpoints.
"""

import pytest
from app.api.main import app
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import uuid

client = TestClient(app)

def test_list_campaigns():
    """Test getting all campaigns."""
    response = client.get("/campaigns")
    assert response.status_code == 200

def test_create_campaign():
    """Test creating a new campaign."""
    mock_campaign_data = {
        "name": "Test Campaign",
        "description": "A test campaign for testing purposes"
    }
    
    response = client.post("/campaigns", json=mock_campaign_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == mock_campaign_data["name"]
    assert data["description"] == mock_campaign_data["description"]

def test_get_campaign_state():
    """Test getting campaign state."""
    # First create a campaign to get its ID  
    campaign_response = client.post("/campaigns", json={
        "name": "State Test Campaign",
        "description": "Testing state endpoint"
    })
    
    assert campaign_response.status_code == 200
    campaign_data = campaign_response.json()
    campaign_id = campaign_data["id"]
    
    # Now test getting the state 
    response = client.get(f"/campaign/{campaign_id}/state")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "stats" in data
    assert "inventory" in data
    assert "location" in data
    assert "characters" in data
    assert "quests" in data

if __name__ == "__main__":
    pytest.main([__file__])