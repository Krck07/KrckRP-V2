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

### Frontend & Campaign API
- `app/static/index.html` - Main frontend HTML: campaign selection and game UI
- `app/static/css/style.css` - CSS styling: responsive design, themes, layout
- `app/static/js/main.js` - UI interactions, SSE handling, API communication
- `app/api/main.py` - *(modified)* New endpoints: `GET /campaigns`, `POST /campaigns`, `GET /campaign/{id}/state`; static file serving
- `app/models/database_models.py` - *(modified)* `DatabaseManager` extended with campaign query/creation methods
- `tests/test_campaign_api.py` - Tests for campaign-related API endpoints
- `tests/test_frontend.py` - Tests for frontend asset accessibility

### Turn Pipeline
- `app/engine/turn_pipeline.py` - Turn Pipeline orchestrator: intent interpretation, mechanics resolution (stub), context assembly (stub), narration, extraction
- `app/engine/__init__.py` - Package initialization exposing key engine components
- `tests/test_turn_pipeline.py` - Tests for the turn pipeline functionality

### Validation & Rewind
- `app/engine/state_manager.py` - *(modified)* Implemented `commit_turn()`, `rewind()`, plus undo/redo (regenerate & edit-past-message) features with validation service integration
- `tests/test_validation_basic.py` - Basic tests for validation and rewind functionality

### Semantic Memory
- `app/memory/semantic_memory.py` - Semantic memory layer: vector storage and retrieval with metadata
- `tests/memory/test_semantic_memory.py` - Unit tests for semantic memory
- `tests/memory/test_semantic_memory_integration.py` - Integration tests for semantic memory with the database
- `app/models/database_models.py` - *(modified)* `DatabaseManager.cleanup_session_entries()` for vector cleanup on session rewind
- `app/engine/state_manager.py` - *(modified)* `rewind()` now session-based (`session_id: uuid.UUID`) and triggers semantic memory cleanup; added `_log_events()`

### Summarizer
- `app/engine/summarizer.py` - Compresses older raw turns into narrative summaries stored in the `Summary` table
- `tests/test_summarizer.py` - Unit tests for the Summarizer module
- `app/models/database_models.py` - *(modified)* Added `campaign_id` field to `GameTurn`; new `DatabaseManager.get_recent_turns()`

### Context Assembly
- `app/engine/turn_pipeline.py` - *(modified)* `_assemble_context()` implemented with strict per-section token budgets and NPC knowledge filtering
- `app/models/database_models.py` - *(modified)* New `DatabaseManager.get_summary_by_campaign()`

### Rules Engine
- `rules_engine.py` *(likely `app/engine/`)* - Main rules engine with deterministic `resolve_action()` evaluation
- `tests/rules_engine_test.py` - Unit tests for the rules engine
- `example_usage.py` - Example usage demonstration
- `README.md` - Module documentation

### Quest Lifecycle & Debug
- `app/engine/quest_lifecycle_manager.py` - Quest state management: proposed → active → completed/failed transitions
- `app/engine/state_manager.py` - *(modified)* `commit_turn()` now processes quest lifecycle events from extractor data
- `app/api/main.py` - *(modified)* New hidden `GET /debug/state` developer endpoint (prompts, extraction results, rejected proposals)
- `app/models/database_models.py` - *(modified)* New `DatabaseManager.get_recent_turns_with_details()`
- `tests/quest_tests/test_quest_lifecycle_manager.py` - Unit tests for QuestLifecycleManager
- `tests/test_api_basic.py` - Basic API endpoint tests
- `tests/test_state_manager_integration.py` - StateManager integration tests

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
│   ├── quest_lifecycle_manager.py
│   ├── rules_engine.py
│   ├── state_manager.py
│   ├── summarizer.py
│   └── turn_pipeline.py
├── static/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── llm/
│   ├── __init__.py  
│   ├── kobold_cpp_client.py
│   ├── extractor.py
│   └── mock_llm.py
└── memory/
    ├── __init__.py
    └── semantic_memory.py

tests/
├── conftest.py
├── fixtures/
│   └── tavern_world.py
├── memory/
│   ├── test_semantic_memory.py
│   └── test_semantic_memory_integration.py
├── quest_tests/
│   └── test_quest_lifecycle_manager.py
├── test_api_basic.py
├── test_campaign_api.py
├── test_frontend.py
├── rules_engine_test.py
├── test_models.py
├── test_state_manager_integration.py
├── test_summarizer.py
├── test_validation_basic.py
├── test_mock_llm.py
└── test_turn_pipeline.py
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
19. **Default World**: Campaigns are tied to a default `world_id` for now; would be parameterized in production
20. **Campaign State**: `GET /campaign/{id}/state` returns character stats, inventory items, location info, and active quests for the UI
21. **Static Serving**: Frontend assets served from `app/static/` via FastAPI static files support
22. **Frontend Design**: Responsive layout (desktop + mobile); JavaScript drives SSE chat updates via `/turn/stream`
23. **Pipeline Workflow**: Interpret Intent → Resolve Mechanics (stub) → Assemble Context → Narrate → Extract
24. **Stub Interfaces**: `ActionResolver` remains a stub; context assembly (`_assemble_context()`) is now implemented (see #41)
25. **Entity Payload**: Known entity IDs/names are prepared in the payload to prevent extraction failures
26. **GBNF Bridge**: `json_schema_to_gbnf()` utility converts Python schema definitions into KoboldCpp grammar
27. **Reuse**: Pipeline builds on existing `DatabaseManager` and `Extractor` components
28. **Async**: All pipeline methods are asynchronous to support LLM integration patterns
29. **Validation**: `ValidationService` checks extracted JSON against actual DB state to ensure consistency before any write
30. **Commit Scope**: `commit_turn()` writes only valid changes to the database and event log
31. **Rewind**: `rewind(session_id)` deletes events from the target point onward and restores exact DB state using `before_value`; now session-based (see #36)
32. **Undo/Redo Semantics**: "Regenerate" = rewind one step (last AI message); "Edit past message" = rewind to a specific turn and replay with new input
33. **Semantic Memory**: Vector storage integrated into the existing SQLite database via sqlite-vec where available
34. **Embeddings**: Currently a simple hashing-based simulation; structured for easy swap to a real model (e.g., Sentence Transformers)
35. **Vector Metadata**: Entries stored with `session_id`, `turn_id`, and other identifiers for tracking and cleanup
36. **Rollback Hooks**: Session rewind deletes associated vector entries via `cleanup_session_entries()`
37. **GameTurn Scope**: `GameTurn` now carries a `campaign_id` field for campaign-scoped filtering
38. **Compression Trigger**: Turn compression runs when at least 2 turns are eligible
39. **Summary Rollback**: Summaries linked via `campaign_id` so they can be rolled back during rewind
40. **Summarization**: Currently placeholder text processing; designed for LLM-based summarization later
41. **Token Budgets**: Strict per-section budgets in context assembly — SQL state ≤600, active quests ≤400, rolling summary ≤400, recent raw turns ≤300, vector memories ≈348 (remaining); sections truncate on overflow
42. **NPC Knowledge Filter**: `_get_vector_memories()` filters retrieved memories by `witness_metadata` so NPCs only "know" memories matching their witness session
43. **Context Structure**: Assembly combines SQL state (characters/locations) + active quests + rolling summary + recent turns + vector memories; all DB calls awaited for async consistency
44. **Difficulty Scale**: Action difficulties are on a 0–100 scale
45. **Stat Normalization**: Stats normalized so 10 = average; higher/lower = better/worse performance
46. **Context Modifiers**: Multiplicative factors (1.0 = no change; >1.0 shifts difficulty/ease) from terrain, inventory, relationships
47. **Roll-Based System**: Probability roll with critical success/failure thresholds; tiers follow standard RPG patterns (critical success → critical failure)
48. **Determinism**: Hash-based seed generation drives the RNG for reproducible outcomes
49. **Stat Weighting**: Per-action stat weighting supported, currently a simplified single approach
50. **Tier as Strict Fact**: Outcome tier is passed to the Context Assembler as a strict fact the Narrator must respect
51. **Quest Lifecycle**: States flow proposed → active → completed/failed; DB persistence of quest states deferred until full schema is defined
52. **Extractor Events**: Structured fields such as `proposed_quests` and `completed_quests` drive lifecycle processing
53. **Debug Endpoint**: `GET /debug/state` is hidden from the normal UI, intended for developer inspection
54. **API Stability**: Existing endpoints remain unchanged; updates only add functionality

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
GameTurn(id: Optional[uuid.UUID], turn_id: int, campaign_id: Optional[uuid.UUID], timestamp: datetime,
         prompt: str, narrative: str, extraction_data: str, status: str, created_at: datetime)
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
POST /turn                    # Game turn: streaming narration + synchronous JSON extraction
GET  /turn/stream             # Server-Sent Events endpoint for real-time turn updates
GET  /health                  # Health check
GET  /campaigns               # Returns list of campaigns
POST /campaigns               # Creates new campaign, returns created campaign
GET  /campaign/{id}/state     # Campaign state for UI: stats, inventory, location, characters, quests
GET  /debug/state             # Hidden dev endpoint: prompts, extraction results, rejected proposals
GET  /                        # Serves the main HTML frontend
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

### Validation Service (`app/engine/state_manager.py`)
```python
ValidationService.__init__(db_manager: DatabaseManager)
ValidationService.validate_extraction(turn_data: Dict, extraction_result: Dict) -> bool
```

### SemanticMemoryManager (`app/memory/semantic_memory.py`)
```python
SemanticMemoryManager.__init__(db_manager: DatabaseManager)
SemanticMemoryManager.embed_text(text: str) -> bytes                      # Embedding vector (simulated)
SemanticMemoryManager.store_with_metadata(content: str, metadata: Dict[str, Any]) -> str  # Returns content hash
SemanticMemoryManager.search_similar(query_text: str, limit: int = 10) -> List[Dict[str, Any]]
SemanticMemoryManager.delete_session_entries(session_id: uuid.UUID) -> None
```

### StateManager (`app/engine/state_manager.py`)
```python
StateManager.__init__(db_manager: DatabaseManager = None)
StateManager.prepare_turn(turn_data: Dict) -> Dict
StateManager.commit_turn(turn_data: Dict, extraction_result: Dict) -> Dict
StateManager.rewind(session_id_to_rewind: uuid.UUID) -> bool   # Rewinds state + cleans up semantic memory
StateManager.regenerate_last_ai_message(turn_id: int) -> bool
StateManager.edit_past_message(turn_id: int, new_input_data: Dict[str, Any]) -> bool
StateManager._log_events(turn_data: Dict[str, Any], extraction_result: Dict[str, Any], session_id: uuid.UUID) -> None
```

### DatabaseManager (`app/models/database_models.py`)
```python
DatabaseManager.save_turn(game_turn: GameTurn) -> None
DatabaseManager.get_turn(turn_id: str) -> Optional[GameTurn]
DatabaseManager.get_all_turns() -> List[GameTurn]

# Campaign operations
DatabaseManager.get_all_campaigns() -> List[Campaign]
DatabaseManager.get_campaign(campaign_id) -> Optional[Campaign]
DatabaseManager.create_campaign(name, description) -> uuid.UUID
DatabaseManager.get_characters_by_campaign(campaign_id) -> List[Character]
DatabaseManager.get_locations_by_campaign(campaign_id) -> List[Location]
DatabaseManager.get_items_by_campaign(campaign_id) -> List[Item]
DatabaseManager.get_quests_by_campaign(campaign_id) -> List[Quest]
DatabaseManager.get_recent_turns(campaign_id: uuid.UUID, limit: int = 10) -> List[GameTurn]
DatabaseManager.get_recent_turns_with_details(campaign_id, limit)    # Detailed turn data incl. extraction info
DatabaseManager.get_summary_by_campaign(campaign_id: uuid.UUID) -> Optional[Summary]

DatabaseManager.cleanup_session_entries(session_id: uuid.UUID) -> None   # Vector entry cleanup on session rewind
```

### Summarizer (`app/engine/summarizer.py`)
```python
Summarizer.__init__(db_manager: DatabaseManager)
Summarizer.compress_turns(campaign_id: UUID, max_turns_to_compress: int = 10) -> Optional[UUID]
Summarizer.get_summary(summary_id: UUID) -> Optional[Summary]

# Internal helpers
Summarizer._get_recent_turns(campaign_id: UUID, max_count: int) -> List[GameTurn]
Summarizer._create_summary_text(turns: List[GameTurn]) -> str
Summarizer._extract_key_elements(narrative: str) -> str
Summarizer._save_summary(campaign_id: UUID, content: str) -> UUID
```

### TurnPipeline (`app/engine/turn_pipeline.py`)
```python
# Data class
Outcome(success: bool, message: str, data: ...)

TurnPipeline.process_turn(raw_input_data)                 # Main entry point
TurnPipeline._interpret_intent(input_data)                 # Interprets player intent from raw input
TurnPipeline._resolve_mechanics(intent)                     # Stub: action resolution (to be expanded)
TurnPipeline._assemble_context(intent, outcome, session_id: uuid.UUID = None) -> str   # Implemented: strict token budgets + NPC knowledge filter
TurnPipeline._prepare_entity_payload(original_input)        # Prepares entity payload to prevent extraction failures
TurnPipeline._get_vector_memories(...)                        # Retrieves memories filtered by witness_metadata (NPC knowledge boundaries)

# Module-level functions
json_schema_to_gbnf(schema, name)   # Converts JSON schema into GBNF grammar
_narrate(context_prompt)            # Placeholder for narrative generation (to be connected with LLM)
_extract(narrative_text, original_input)  # Extracts structured data from narratives
```

### QuestLifecycleManager (`app/engine/quest_lifecycle_manager.py`)
```python
QuestLifecycleManager.handle_extractor_events(turn_data, extraction_result)   # Processes quest lifecycle events
```

### Rules Engine (`rules_engine.py`)
```python
# Types
OutcomeTier(Enum)                    # Action outcome categories
ActionContext(dataclass)             # Contextual modifiers: terrain, inventory, relationships
CharacterStats(dataclass)            # Player character statistics
ActionEvaluation(dataclass)          # Result of action evaluation
RulesEngine                          # Main rules engine class

# Core function (deterministic)
resolve_action(action_difficulty: float, character_stats: CharacterStats, context: ActionContext) -> ActionEvaluation
```

This foundational work sets up the framework for implementing the core engine components while maintaining alignment with all requirements specified in KrckRP-Requirements.md.