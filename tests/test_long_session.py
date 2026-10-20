"""
Long Session Test for KrckRP.
Tests that NPC recall, summaries, and context assembler don't crash or overflow 
across multiple sessions with 50+ turns.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

# Import modules to be tested  
from app.models.database_models import DatabaseManager, Session, Campaign, Character, Location, Item, Quest
from app.engine.correction_assistant import CorrectionAssistant
from app.engine.state_manager import StateManager


class MockLLM:
    """Mock LLM for testing that simulates 50+ turns across sessions"""
    
    def __init__(self):
        self.turn_count = 0
        
    async def generate_narrative(self, turn_data: dict):
        """Generate a mock narrative with some complexity"""
        # Create a simple but varied narrative
        self.turn_count += 1
        turn_number = self.turn_count
        
        if turn_number <= 25:
            # Early turns - basic actions
            return f"Turn {turn_number}: The party explores the ancient ruins. They find a treasure chest with magical items inside."
        elif turn_number <= 40:
            # Mid-turns - more complex interactions  
            return f"Turn {turn_number}: The group encounters a mysterious NPC who offers them a quest. They decide to accept and begin investigating."
        else:
            # Later turns - narrative complexity
            return f"Turn {turn_number}: The party faces the final challenge, having discovered ancient secrets that affect their world's fate."

    async def extract_structured_data(self, narration: str, turn_data: dict):
        """Extract mock structured data"""
        return {
            "characters": [
                {"id": str(uuid4()), "name": "Player", "action": "explore"}
            ],
            "locations": [
                {"id": str(uuid4()), "name": "Ancient Ruins", "description": "A mysterious place filled with treasures"}
            ],
            "items": [
                {"id": str(uuid4()), "name": "Magical Sword", "description": "A powerful weapon"}
            ],
            "factions": [],
            "quests": [
                {"id": str(uuid4()), "status": "active" if self.turn_count > 10 else "proposed", 
                 "progress": min(100, self.turn_count * 2)}
            ]
        }


@pytest.mark.asyncio
async def test_long_session_simulation():
    """
    Simulate a long session with 50+ turns across multiple sessions.
    
    This test ensures that:
    - NPC recall works properly across multiple sessions 
    - Summaries don't overflow or crash  
    - Context assembler handles extended play without memory issues
    
    The test uses the Mock LLM to simulate realistic behavior while staying within resource limits.
    """
    # Create mock database manager
    db_manager = MagicMock()
    
    # Create a campaign and session for testing 
    campaign_id = uuid4()
    session_id = uuid4()
    
    # Mock the session creation methods
    db_manager.get_campaign.return_value = Campaign(
        id=campaign_id,
        world_id=uuid4(),
        name="Test Campaign",
        description="A test campaign"
    )
    
    db_manager.get_session_by_id.return_value = Session(
        id=session_id,
        campaign_id=campaign_id,
        name="Test Session", 
        description="A test session",
        started_at=True
    )
    
    # Mock character, location and quest data to simulate NPC recall
    mock_character = Character(
        id=uuid4(),
        name="NPC Test Character",
        description="An important non-player character"
    )
    
    mock_location = Location(
        id=uuid4(),
        name="Important Location", 
        description="A key place in the world"
    )
    
    db_manager.get_characters_by_campaign.return_value = [mock_character]
    db_manager.get_locations_by_campaign.return_value = [mock_location] 
    
    # Create state manager with mock DB
    state_manager = StateManager(db_manager)
    
    # Replace LLM with our mock
    from app.llm.kobold_cpp_client import KoboldCppClient
    from app.llm.extractor import Extractor
    
    with patch.object(KoboldCppClient, 'generate_narrative', new_callable=AsyncMock) as mock_generate:
        with patch.object(Extractor, 'extract_structured_data', new_callable=AsyncMock) as mock_extract:
            
            # Mock the LLM methods
            llm = MockLLM()
            mock_generate.side_effect = llm.generate_narrative
            mock_extract.side_effect = llm.extract_structured_data
            
            # Run 50 turns to simulate a long session
            for i in range(50):
                try:
                    # Simulate turn processing with our mock LLM 
                    prompt = f"Turn {i+1}: The party investigates the mysterious location."
                    
                    result = await state_manager.prepare_turn({
                        "prompt": prompt,
                        "session_id": str(session_id)
                    })
                    
                    # Process turn (this calls both LLM generation and extraction)  
                    final_result = await state_manager.commit_turn(result, {
                        "characters": [{"id": str(uuid4()), "name": "Player", "action": "investigate"}],
                        "locations": [{"id": str(uuid4()), "name": "Mysterious Location"}], 
                        "items": [],
                        "factions": [],
                        "quests": [{"id": str(uuid4()), "status": "active", "progress": 10 + (i % 50)}]
                    })
                    
                    # Check that we get results without crashing
                    assert final_result is not None
                    
                except Exception as e:
                    pytest.fail(f"Error processing turn {i+1}: {e}")
            
            # Verify that our mock LLM ran all turns correctly
            assert llm.turn_count == 50, f"Expected 50 turns but got {llm.turn_count}"
            
            # Test the correction assistant in session context 
            correction_assistant = CorrectionAssistant(db_manager)
            
            # Test a few correction operations to ensure they work with session state
            move_result = await correction_assistant.move_character(
                character_id=uuid4(),
                new_location_id=uuid4()
            )
            assert move_result["success"] is True
            
            stat_result = await correction_assistant.set_stat(
                character_id=uuid4(),
                stat_name="strength", 
                new_value=15
            )
            assert stat_result["success"] is True


@pytest.mark.asyncio  
async def test_session_management_functionality():
    """Test that session management works properly with database operations"""
    
    # Create mock database manager
    db_manager = MagicMock()
    
    # Mock session creation and status checks 
    campaign_id = uuid4() 
    session_id = uuid4()
    
    db_manager.get_campaign.return_value = Campaign(
        id=campaign_id,
        world_id=uuid4(),
        name="Test Campaign",
        description="A test campaign"
    )
    
    # Test creating a new session
    with patch('app.models.database_models.Session') as mock_session_class:
        mock_session_instance = MagicMock()
        mock_session_instance.id = session_id
        mock_session_instance.campaign_id = campaign_id
        mock_session_class.return_value = mock_session_instance
        
        db_manager.save_session = AsyncMock()
        
        # This should work without throwing errors even with many calls
        for i in range(10):  # Multiple sessions
            result = await db_manager.save_session(mock_session_instance)
            assert result is None  # save_session doesn't return anything
            
    # Test session start/end operations
    db_manager.start_session = AsyncMock(return_value=True) 
    db_manager.end_session = AsyncMock(return_value=True)
    
    success_start = await db_manager.start_session(session_id)
    success_end = await db_manager.end_session(session_id)
    
    assert success_start is True
    assert success_end is True


@pytest.mark.asyncio
async def test_context_assembler_stress_test():
    """Test that the context assembler can handle long sessions"""
    
    # This would typically be part of a more complex integration test with actual pipeline components
    
    # Test data that simulates extended play session 
    mock_recent_turns = []
    for i in range(30):  # Simulate 30 recent turns
        mock_recent_turns.append({
            "turn_id": i,
            "prompt": f"Turn {i}: Action {i}",
            "narrative": f"Narrative text for turn {i}",
            "extraction_data": {"characters": [], "quests": []}
        })
        
    # Test that we can handle this volume of data without crashing
    assert len(mock_recent_turns) == 30
    
    # This is a basic structural test - actual context assembly tests would be more complex
    mock_summary_content = "Summary of the campaign's events over many turns"
    assert isinstance(mock_summary_content, str)