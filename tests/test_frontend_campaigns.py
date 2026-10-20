"""
Tests for campaign loading functionality on frontend.
"""

import pytest
from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_campaign_list_endpoint_returns_valid_data():
    """Test that /campaigns endpoint returns valid JSON structure."""
    response = client.get("/campaigns")
    assert response.status_code == 200
    
    # Verify it's valid JSON
    data = response.json()
    
    # Should be a list (even if empty)
    assert isinstance(data, list)
    
def test_campaign_list_endpoint_with_data():
    """Test campaign listing with actual data."""
    # First create a campaign to have something to return
    campaign_data = {
        "name": "Test Campaign",
        "description": "A test campaign for frontend testing"
    }
    
    response = client.post("/campaigns", json=campaign_data)
    assert response.status_code == 200
    
    # Now check that we can list campaigns
    response = client.get("/campaigns")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    
    if len(data) > 0:
        campaign = data[0]
        # Check required fields are present
        assert "id" in campaign
        assert "name" in campaign
        assert "description" in campaign
        assert "created_at" in campaign
        assert "world_clock" in campaign
        
    # Clean up by deleting the test campaign if it was created
    try:
        campaign_id = response.json()[0]["id"] if response.json() else None
        if campaign_id:
            client.delete(f"/campaign/{campaign_id}")
    except:
        pass  # Ignore cleanup errors

if __name__ == "__main__":
    pytest.main([__file__, "-v"])