"""
Basic tests to ensure core API functionality works.
"""

import pytest
from fastapi.testclient import TestClient

# Import the main app  
from app.api.main import app


class TestAPIBasic:
    """Test basic API functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        
    def test_health_endpoint(self):
        """Test that health endpoint works."""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
    def test_debug_endpoint_exists(self):
        """Test that debug endpoint is registered."""
        response = self.client.get("/debug/state?campaign_id=123e4567-e89b-12d3-a456-426614174000")
        # This should return a valid JSON structure even if it's just placeholder data
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])