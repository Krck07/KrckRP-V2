"""
Tests for the Debug API endpoints.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest

# Import modules we're testing
from app.api.main import app
from fastapi.testclient import TestClient


class TestDebugAPI:
    """Test cases for debug API functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = TestClient(app)
        
    @pytest.mark.asyncio
    async def test_debug_state_endpoint(self):
        """Test the debug state endpoint returns expected structure."""
        # We'll mock database calls to avoid actual DB interactions
        
        response = self.client.get("/debug/state?campaign_id=123e4567-e89b-12d3-a456-426614174000")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the structure of the returned debug information
        assert "campaign_id" in data
        assert "last_turns" in data  
        assert "extractor_results" in data
        assert "rejected_proposals" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])