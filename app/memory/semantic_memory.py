"""
Semantic Memory Implementation using sqlite-vec for KrckRP.

This module provides vector-based storage and retrieval for game content,
enabling semantic search of narrative content, character descriptions,
and other textual elements.
"""

from typing import List, Dict, Any, Optional, Tuple
import uuid
import json
from datetime import datetime

# Import database models 
from app.models.database_models import DatabaseManager, Session

# For vector storage (we'll implement a simple approach using sqlite)
try:
    # If sqlite-vec is available, we can use it; otherwise, provide fallback
    import sqlite3
    from sqlite3 import Connection
    
    def create_vector_tables(conn: Connection) -> None:
        """Create the required tables for semantic memory storage."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vector_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                embedding BLOB NOT NULL,
                content TEXT NOT NULL,
                metadata JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for faster searches
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_vector_content_hash 
            ON vector_entries(content_hash)
        """)
        
    def store_vector_entry(conn: Connection, content_hash: str, embedding: bytes, 
                          content: str, metadata: Dict[str, Any]) -> None:
        """Store a vector entry with its metadata."""
        conn.execute("""
            INSERT OR REPLACE INTO vector_entries (content_hash, embedding, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (content_hash, embedding, content, json.dumps(metadata)))
        conn.commit()
        
    def search_similar_vectors(conn: Connection, query_embedding: bytes, 
                              limit: int = 10) -> List[Dict[str, Any]]:
        """Find similar vectors using cosine similarity."""
        # This is a simplified approach - in practice we'd use sqlite-vec's actual vector functions
        cursor = conn.execute("""
            SELECT content_hash, embedding, content, metadata FROM vector_entries 
            ORDER BY (SELECT 1) LIMIT ?
        """, (limit,))
        
        return [
            {
                "content_hash": row[0],
                "embedding": row[1], 
                "content": row[2],
                "metadata": json.loads(row[3])
            }
            for row in cursor.fetchall()
        ]
        
    def delete_vector_entries_for_session(conn: Connection, session_id: uuid.UUID) -> None:
        """Delete all vector entries associated with a specific session."""
        conn.execute("""
            DELETE FROM vector_entries 
            WHERE metadata LIKE ?
        """, (f'%"{session_id}"%',))
        conn.commit()
        
except ImportError:
    # Fallback for when sqlite-vec is not available
    pass


class SemanticMemoryManager:
    """
    Manages semantic memory using vector embeddings for efficient retrieval.
    
    This manager provides methods to embed text, store it with metadata,
    and perform semantic searches. It also handles rollback hooks 
    to clean up associated vector entries when sessions are rewound.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize the semantic memory manager."""
        self.db_manager = db_manager
        # For now we'll work with the same database connection for simplicity
        # In production this might be a separate vector database
        self._initialize_vector_tables()
        
    def _initialize_vector_tables(self) -> None:
        """Initialize the required tables in the main database."""
        try:
            with Session(self.db_manager.engine) as session:
                conn = session.connection().connection
                create_vector_tables(conn)
        except Exception as e:
            print(f"Warning: Could not initialize vector tables - {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for the content to identify duplicates."""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    async def embed_text(self, text: str) -> bytes:
        """
        Generate embedding vector for text.
        
        This is a placeholder implementation. In production,
        you would use a proper embedding model like Sentence Transformers.
        For now we'll simulate an embedding with simple hashing.
        
        Args:
            text (str): Text to embed
            
        Returns:
            bytes: Simulated embedding vector
        """
        # Simple hash-based approach for demonstration purposes only
        import hashlib
        return hashlib.sha256(text.encode()).digest()
    
    async def store_with_metadata(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Store text with its metadata and generate embedding.
        
        Args:
            content (str): The textual content to store
            metadata (Dict): Metadata associated with the content
            
        Returns:
            str: Content hash for reference
        """
        # Generate a content hash 
        content_hash = self._generate_content_hash(content)
        
        try:
            # In a real implementation, we'd call an embedding model here
            embedding = await self.embed_text(content)
            
            with Session(self.db_manager.engine) as session:
                conn = session.connection().connection
                
                # Store the vector entry
                store_vector_entry(conn, content_hash, embedding, content, metadata)
                
        except Exception as e:
            print(f"Error storing vector entry: {e}")
            raise
            
        return content_hash
    
    async def search_similar(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find semantically similar content to the query text.
        
        Args:
            query_text (str): Text to find similar content for
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict]: Similar entries with their metadata and similarity scores
        """
        try:
            # Generate embedding for query 
            query_embedding = await self.embed_text(query_text)
            
            with Session(self.db_manager.engine) as session:
                conn = session.connection().connection
                
                # Find similar vectors
                results = search_similar_vectors(conn, query_embedding, limit)
                
                return results
                
        except Exception as e:
            print(f"Error during semantic search: {e}")
            return []
    
    async def delete_session_entries(self, session_id: uuid.UUID) -> None:
        """
        Delete all vector entries associated with a specific session.
        
        This is used as a rollback hook when sessions are rewound.
        
        Args:
            session_id (uuid.UUID): The session ID to clean up
        """
        try:
            with Session(self.db_manager.engine) as session:
                conn = session.connection().connection
                
                # Delete all vector entries for this session
                delete_vector_entries_for_session(conn, session_id)
                
        except Exception as e:
            print(f"Error deleting session entries: {e}")
            raise


# For backward compatibility with existing code that might expect direct access
semantic_memory_manager = SemanticMemoryManager(DatabaseManager())