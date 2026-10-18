# KrckRP Interface Documentation

## Created Files

### Foundation Documents
- `RULES.md` - Defines the default stat set, numeric scales, resolution formula, outcome tier thresholds, and capability modifiers
- `API_CONTRACT.md` - Documented all public endpoints for communication between frontend and backend with request/response formats  
- `KOBOLD_CHEAT_SHEET.md` - Documents KoboldCpp streaming endpoint and grammar (GBNF) submission format

### Project Structure Scripts
- `scaffold_project.sh` - Shell script to create the directory structure

### Implementation & Tests
- `app/models/database_models.py` - All database models: World, Campaign, Session, Character, Location, Item, Faction, Ability, Quest, Summary, Relationship, EventLog
- `app/models/__init__.py` - Package initialization exposing all models
- `app/llm/mock_llm.py` - Mock LLM client (`generate_narration()`, `extract_json()`, `generate_response()`)
- `tests/fixtures/tavern_world.py` - Sample tavern world fixture for database population tests
- `tests/test_models.py` - Tests for the database models
- `tests/test_mock_llm.py` - Tests for the mock LLM client
- `tests/conftest.py` - Test configuration

### API & Engine Implementation
- `app/api/main.py` - FastAPI application with `POST /turn`, `GET /turn/stream` (SSE), and `GET /health` endpoints
- `app/llm/kobold_cpp_client.py` - KoboldCpp HTTP client wrapper with streaming and mock-fallback capabilities
- `app/llm/extractor.py` - JSON grammar extraction module
- `app/engine/state_manager.py` - Game state manager; database commits only after successful narrative generation AND data extraction
- `app/models/database_models.py` - *(modified)* Added `GameTurn` model and `DatabaseManager` class

## Directory Structure Created

```
app/
├── __init__.py
├── api/
│   └── main.py
├── models/
│   ├── __init__.py
│   └── database_models.py
├── engine/ 
│   ├── __init__.py
│   └── state_manager.py
├── llm/
│   ├── __init__.py  
│   ├── kobold_cpp_client.py
│   ├── extractor.py
│   └── mock_llm.py
└── memory/
    └── __init__.py

tests/
├── conftest.py
├── fixtures/
│   └── tavern_world.py
├── test_models.py
└── test_mock_llm.py
```

## Core Assumptions

1. **Vector Store**: Using sqlite-vec as specified in requirements for keeping everything in one DB ecosystem
2. **Streaming Protocol**: Server-Sent Events (SSE) for UI streaming as per requirements  
3. **Resolution Engine**: Strictly deterministic with minimal randomness, using capability vs difficulty formula
4. **Data Model**: Follows the core entities defined in KrckRP-Requirements.md (World, Campaign, Character, Location, Item, Ability, Faction, Relationship, Quest, Event, Turn, Session)
5. **Architecture**: Engine sits between player and LLMs with clear separation of concerns - engine handles game logic, LLMs handle language generation
6. **API Design**: RESTful endpoints with streaming capabilities for real-time updates
7. **Primary Keys**: UUIDs used across all models for scalability and consistency
8. **Foreign Keys**: Entities linked via proper FK relationships (e.g., Campaign → World, Character → Campaign); Relationships implemented with SQLModel `Relationship` for bidirectional access
9. **World Clock**: `Campaign.world_clock` implemented as `datetime` to track in-campaign time
10. **Audit Trail**: `EventLog` captures before/after values for field-level change tracking
11. **Timestamps**: All models carry a `created_at` timestamp
12. **Mock LLM**: Returns keyword-based canned responses to simulate real behavior during testing
13. **Layout**: Standard Python package layout with `app/` as the main application directory
14. **KoboldCpp Service**: Expected running on default port 5000 with `/generate` and `/extract` endpoints
15. **Database Connection**: Defaults to SQLite for development (`sqlite:///./test.db`); all operations via SQLModel `Session` management
16. **Transactional Integrity**: State changes commit only after both narrative generation and data extraction succeed (commits happen after the narrator stream ends)
17. **Fallback**: Mock implementations kick in automatically when KoboldCpp is unavailable
18. **Turn Structure**: Game turns carry a consistent structure with `prompt`, `max_tokens`, and `temperature` fields

## Key Technical Decisions

1. **Storage**: SQLite for both relational data and vector store (using sqlite-vec)
2. **LLM Interface**: KoboldCpp HTTP API with GBNF grammar constraints  
3. **Frontend Protocol**: Server-Sent Events for streaming responses
4. **Rules Engine**: Deterministic resolution system with outcome tiers
5. **Memory Management**: Multi-tier approach (working, rolling summary, canonical facts, episodic memory, lore)

## Public Interface Signatures

### RULES.md
- Defines core stat set: Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma
- Specifies numeric scales from 1-20 with modifiable range to 30  
- Provides resolution formula for outcome tier calculation
- Includes capability modifiers and context-based adjustments

### API_CONTRACT.md 
- HTTP endpoints for world/campaign management
- Character and location management APIs
- Action processing with streaming response capabilities
- Memory/context retrieval functionality
- Event management (undo/redo operations)

### KOBOLD_CHEAT_SHEET.md
- KoboldCpp endpoint structure and request format
- Streaming SSE protocol usage 
- GBNF grammar definition patterns for JSON constraints
- Parameter settings for narrator vs extractor models

### Database Models (`app/models/database_models.py`)
```python
World(id: Optional[uuid.UUID], name: str, description: str)
Campaign(id: Optional[uuid.UUID], world_id: uuid.UUID, name: str, description: str, world_clock: datetime)
Session(id: Optional[uuid.UUID], campaign_id: uuid.UUID, name: str, description: str)
Character(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Location(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Item(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Faction(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Ability(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Quest(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Summary(id: Optional[uuid.UUID], content: str, campaign_id: uuid.UUID)
Relationship(id: Optional[uuid.UUID], character_id: uuid.UUID, related_character_id: uuid.UUID, relationship_type: str)
EventLog(id: Optional[uuid.UUID], turn_id: int, entity_type: str, entity_id: uuid.UUID, field: str,
        operation: str, before_value: Optional[str], after_value: Optional[str],
        sequence_num: int, witness_metadata: str)
```

### Mock LLM Client (`app/llm/mock_llm.py`)
```python
MockLLMClient.__init__()
MockLLMClient.generate_narration(prompt: str) -> str
MockLLMClient.extract_json(prompt: str) -> Dict[str, Any]
MockLLMClient.generate_response(prompt: str) -> Dict[str, Any]
```

### Test Fixture (`tests/fixtures/tavern_world.py`)
```python
create_tavern_world_fixture() -> Dict[str, uuid.UUID]
```

### FastAPI App (`app/api/main.py`)
```python
POST /turn        # Game turn: streaming narration + synchronous JSON extraction
GET  /turn/stream # Server-Sent Events endpoint for real-time turn updates
GET  /health      # Health check
```

### KoboldCppClient (`app/llm/kobold_cpp_client.py`)
```python
KoboldCppClient.__init__(base_url: str, timeout: int)
KoboldCppClient.is_healthy() -> bool
KoboldCppClient.generate_narrative(turn_data: Dict) -> AsyncGenerator[str]
KoboldCppClient.extract_json(text: str, schema: Dict) -> Dict
```

### Extractor (`app/llm/extractor.py`)
```python
Extractor.__init__()
Extractor.extract_structured_data(narrative_text: str, turn_data: Dict) -> Dict
```

### StateManager (`app/engine/state_manager.py`)
```python
StateManager.__init__(db_manager: DatabaseManager = None)
StateManager.prepare_turn(turn_data: Dict) -> Dict
StateManager.commit_turn(turn_data: Dict, extraction_result: Dict) -> Dict
```

### DatabaseManager (`app/models/database_models.py`)
```python
DatabaseManager.save_turn(game_turn: GameTurn) -> None
DatabaseManager.get_turn(turn_id: str) -> Optional[GameTurn]
DatabaseManager.get_all_turns() -> List[GameTurn]
```

### GameTurn Model (`app/models/database_models.py`)
```python
GameTurn(id, turn_id, timestamp, prompt: str, narrative: str, extraction_data, status, created_at)
```

This foundational work sets up the framework for implementing the core engine components while maintaining alignment with all requirements specified in KrckRP-Requirements.md.