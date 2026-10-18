"""
Tests for the frontend functionality.
"""

import pytest
from app.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root_endpoint():
    """Test that the root endpoint returns our HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
def test_static_files():
    """Test that static files are accessible."""
    # Test CSS file
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    
    # Test JS file  
    response = client.get("/static/js/main.js")
    assert response.status_code == 200
    assert "application/javascript" in response.headers["content-type"]

if __name__ == "__main__":
    pytest.main([__file__])