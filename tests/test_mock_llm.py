import pytest
from app.llm.mock_llm import MockLLMClient


def test_mock_llm_client_creation():
    """Test that the MockLLMClient can be created."""
    client = MockLLMClient()
    assert isinstance(client, MockLLMClient)


def test_mock_llm_generate_narration():
    """Test that the mock LLM generates narrations."""
    client = MockLLMClient()
    
    # Test with tavern prompt
    narration = client.generate_narration("Enter the tavern")
    assert isinstance(narration, str)
    assert len(narration) > 0
    
    # Test with character prompt
    narration = client.generate_narration("Meet a mysterious NPC")
    assert isinstance(narration, str)
    assert len(narration) > 0


def test_mock_llm_extract_json():
    """Test that the mock LLM extracts JSON."""
    client = MockLLMClient()
    
    # Test character extraction
    extracted_data = client.extract_json("Describe a brave warrior")
    assert isinstance(extracted_data, dict)
    assert "name" in extracted_data
    
    # Test item extraction
    extracted_data = client.extract_json("Find a magical sword")
    assert isinstance(extracted_data, dict)
    assert "name" in extracted_data


def test_mock_llm_generate_response():
    """Test that the mock LLM generates full responses."""
    client = MockLLMClient()
    
    response = client.generate_response("Enter the tavern")
    assert "narration" in response
    assert "extracted_data" in response
    assert isinstance(response["narration"], str)
    assert isinstance(response["extracted_data"], dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])