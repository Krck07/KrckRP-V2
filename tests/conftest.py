"""
Test configuration for KrckRP tests.
"""

import pytest
from sqlmodel import create_engine, SQLModel
from app.models.database_models import World, Campaign, Session as SessionModel


@pytest.fixture(scope="session")
def test_db():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_db):
    """Create a new database session for each test."""
    from sqlmodel import Session
    with Session(test_db) as session:
        yield session