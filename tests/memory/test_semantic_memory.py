"""
Tests for the semantic memory implementation.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

# Import our modules 
from app.memory.semantic_memory import SemanticMemoryManager
from app.models.database_models import DatabaseManager


@pytest.fixture
def mock_db_manager():
    """Create a mock database manager."""
    db_manager = MagicMock()
    return db_manager


@pytest.fixture
def semantic_memory_manager(mock_db_manager):
    """Create a semantic memory manager instance."""
    return SemanticMemoryManager(mock_db_manager)


class TestSemanticMemoryManager:
    
    def test_init(self, semantic_memory_manager, mock_db_manager):
        """Test that the semantic memory manager initializes correctly."""
        assert semantic_memory_manager.db_manager == mock_db_manager
        
    async def test_embed_text(self, semantic_memory_manager):
        """Test text embedding functionality."""
        # This is a simple test - in reality this would use an embedding model
        content = "This is a test sentence for embedding."
        embedding = await semantic_memory_manager.embed_text(content)
        
        assert isinstance(embedding, bytes)
        assert len(embedding) > 0
        
    async def test_store_with_metadata(self, semantic_memory_manager):
        """Test storing text with metadata."""
        # Mock the database operations
        content = "This is test content for storage."
        metadata = {
            "turn_id": 1,
            "session_id": "test-session-id",
            "characters_present": ["Alice", "Bob"]
        }
        
        # This would normally call a vector store, but we're testing the interface
        hash_result = await semantic_memory_manager.store_with_metadata(content, metadata)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0
        
    async def test_search_similar(self, semantic_memory_manager):
        """Test searching for similar content."""
        # This is a placeholder - actual implementation would require vector database
        query_text = "test query"
        results = await semantic_memory_manager.search_similar(query_text)
        
        assert isinstance(results, list)


# Test cleanup functionality (this requires integration with DatabaseManager)
class TestSemanticMemoryCleanup:
    
    async def test_delete_session_entries(self, semantic_memory_manager):
        """Test that session entries can be deleted."""
        # This tests the interface for deletion
        session_id = "test-session-id"
        
        # Mock the database method call
        await semantic_memory_manager.delete_session_entries(session_id)
        
        # We just verify it doesn't raise an error - actual implementation would require 
        # real vector store integration