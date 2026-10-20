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
- `app/api/main.py` - *(modified)* New endpoints: `GET /campaigns`, `POST /campaigns`, `GET /campaign/{id}/state`; static file serving; added `/world/form` and `/character/create`
- `app/static/world_form.html` - World form editor HTML page
- `app/static/js/form_editor.js` - JavaScript for world editing UI
- `app/static/character_creator.html` - Character creator HTML page
- `app/static/js/character_creator.js` - JavaScript for character creation UI
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

### World Creation
- `app/api/world_creation.py` - API module for chat-based world creation endpoints
- `app/models/world_models.py` - World template definitions with `to_dict()`/`from_dict()` and `WORLD_SCHEMA` validation
- `app/engine/campaign_initializer.py` - Campaign initializer that creates campaign entities from world templates  
- `tests/test_world_creation.py` - Tests for world creation functionality
- `tests/test_campaign_initializer.py` - Tests for the campaign initialization process
- `app/models/__init__.py` - *(modified)* Exports new world models

### SqlModel Fixes & Seed
- `app/models/world_models.py` - *(modified)* Renamed `World` class to `WorldTemplate` to resolve naming conflict with the SQLModel `World` entity
- `app/models/database_models.py` - *(modified)* Fixed SqlModel usage patterns and datetime handling
- `app/api/main.py` - *(modified)* Updated imports for renamed world model
- `app/api/world_creation.py` - *(modified)* Updated imports for renamed world model
- `seed_dp.py` - Seed script enhanced to work with SqlModel table creation
- `tests/test_database_models.py` - Comprehensive test suite for database models (all passing)

### Correction Assistant & Session Management
- `app/engine/correction_assistant.py` - Implements safe correction tools (move_character, set_stat, give_item, update_quest) with strict tool whitelisting and no raw SQL access
- `app/static/manual_data_editor.html` - Manual Data Editor UI for direct database form editing  
- `app/static/js/manual_data_editor.js` - JavaScript implementation for the manual data editor UI
- `app/api/main.py` - *(modified)* New endpoints: POST /api/sessions, POST /api/sessions/{session_id}/start, POST /api/sessions/{session_id}/end, POST /api/correction/{tool_name}
- `app/models/database_models.py` - *(modified)* Extended Session model with started_at and ended_at fields; added start_session(), end_session(), get_active_sessions(), get_session_by_id() methods
- `tests/test_long_session.py` - Long-Session test: NPC recall across multiple sessions, summary handling without overflow, context assembler stability over 50+ turns
- `app/engine/correction_assistant.py` - *(modified)* Every tool execution writes an EventLog entry with `source="assistant_correction"` (via `witness_metadata`); added `get_available_tools()`
- `app/engine/state_manager.py` - *(modified)* `rewind()` restores database state by parsing EventLog entries and applying `before_value` per operation type (UPDATE, INSERT, DELETE)
- `app/models/database_models.py` - *(modified)* New event logging/restoration methods: `log_event()`, `get_events_for_session()`, `delete_events_for_session()`
- `tests/test_correction_assistant.py` - Unit tests for the correction assistant tools and EventLog integration

## Directory Structure Created

```
seed_dp.py

app/
├── __init__.py
├── api/
│   ├── main.py
│   └── world_creation.py
├── models/
│   ├── __init__.py
│   ├── database_models.py
│   └── world_models.py
├── engine/
│   ├── __init__.py
│   ├── quest_lifecycle_manager.py
│   ├── rules_engine.py
│   ├── state_manager.py
│   ├── campaign_initializer.py
│   ├── correction_assistant.py
│   └── turn_pipeline.py
├── static/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── main.js
│   │   ├── form_editor.js
│   │   ├── character_creator.js
│   │   └── manual_data_editor.js
│   ├── world_form.html
│   ├── character_creator.html
│   └── manual_data_editor.html
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
├── test_database_models.py
├── test_state_manager_integration.py
├── test_summarizer.py
├── test_world_creation.py
├── test_validation_basic.py
├── test_mock_llm.py
├── test_turn_pipeline.py
├── test_correction_assistant.py
├── test_campaign_initializer.py
└── test_long_session.py
```

## Core Assumptions

1. **Form Editor / Character Creator UI**: draft data is persisted in browser local storage during editing (temporary persistence, not the database)
2. **Campaign Initializer**: creates all template entities (locations, factions, characters — NPCs + player — and abilities) and sets up an initial session for the new campaign
3. **Character creation** can be performed independently of the world creation flow
4. **Context Assembly token budgets** (per section, truncated when exceeded): SQL state 600, active quests 400, rolling summary 400, recent raw turns 300, vector memories get the remainder (approx. 348)
5. **Correction Assistant**: all database modifications go through the 4 whitelisted safe tools (`move_character`, `set_stat`, `give_item`, `update_quest`) — never raw SQL; the design is extensible for future tool additions
6. **Session lifecycle**: sessions are started/ended with timestamp tracking (`started_at`/`ended_at`), and active sessions are queryable; session tracking underpins long-session stability (NPC recall, summary overflow prevention)
7. **Correction audit trail**: every correction tool execution explicitly writes an EventLog record with `source="assistant_correction"` (stored in `witness_metadata` to distinguish it from other sources), using `before_value`/`after_value` so rewind can restore exact state
8. **Rewind restoration**: `rewind()` parses EventLog entries and applies `before_value` to entities based on operation type (UPDATE, INSERT, DELETE); database operations follow SQLAlchemy session management with commit/rollback error handling and no breaking changes to existing models
9. **Model naming**: the world *template* model is `WorldTemplate` (renamed from `World` in `world_models.py`) to avoid conflict with the SQLModel `World` entity in `database_models.py`; all API imports were updated accordingly
10. **SqlModel usage**: database models use the real working SqlModel dependency from the project virtual environment (with corrected datetime handling); the seed script creates tables and populates data via the ORM

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
- World form editor (`GET /world/form`)
- Character creator flow (`GET /character/create`)

### KOBOLD_CHEAT_SHEET.md
- KoboldCpp endpoint structure and request format
- Streaming SSE protocol usage 
- GBNF grammar definition patterns for JSON constraints
- Parameter settings for narrator vs extractor models

### Database Models (`app/models/database_models.py`)
```python
World(id: Optional[uuid.UUID], name: str, description: str)
Campaign(id: Optional[uuid.UUID], world_id: uuid.UUID, name: str, description: str, world_clock: datetime)
Session(id: Optional[uuid.UUID], campaign_id: uuid.UUID, name: str, description: str, started_at: Optional[datetime], ended_at: Optional[datetime])
Character(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Location(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Item(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Faction(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Ability(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Quest(id: Optional[uuid.UUID], name: str, description: str, campaign_id: uuid.UUID)
Summary(id: Optional[uuid.UUID], content: str, campaign_id: uuid.UUID)
Relationship(id: Optional[uuid.UUID], character_id: uuid.UUID, related_character_id: uuid.UUID, relationship_type: str)
EventLog(id: Optional[uuid.UUID], turn_id: int, session_id: uuid.UUID, entity_type: str, entity_id: uuid.UUID, field: str, operation: str, before_value: Optional[str], after_value: Optional[str], sequence_num: int, witness_metadata: str, created_at: datetime)
GameTurn(id: Optional[uuid.UUID], turn_id: int, timestamp: datetime, prompt: str, narrative: str, extraction_data: str, status: str, created_at: datetime, campaign_id: Optional[uuid.UUID])
DatabaseManager
```

### Engine Components

#### CorrectionAssistant (`app/engine/correction_assistant.py`)
```python
class CorrectionAssistant:
    async def move_character(self, character_id: UUID, new_location_id: UUID) -> Dict[str, Any]
    async def set_stat(self, character_id: UUID, stat_name: str, new_value: int) -> Dict[str, Any]  
    async def give_item(self, character_id: UUID, item_id: UUID) -> Dict[str, Any]
    async def update_quest(self, quest_id: UUID, status: str = None, progress: int = None) -> Dict[str, Any]
    def get_available_tools(self) -> List[str]   # Returns the whitelisted tool names
    
# Every tool execution writes an EventLog entry with source="assistant_correction" (witness_metadata)
# and before_value/after_value so rewind() can restore the exact prior state

class CorrectionAssistantAPI:
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]
```

#### Session Management (`app/models/database_models.py`)
```python
async def start_session(self, session_id: uuid.UUID) -> bool
async def end_session(self, session_id: uuid.UUID) -> bool
async def get_active_sessions(self) -> List[Session]
async def get_session_by_id(self, session_id: uuid.UUID) -> Optional[Session]
```

#### API Endpoints (`app/api/main.py`)
```http
POST /api/sessions
POST /api/sessions/{session_id}/start  
POST /api/sessions/{session_id}/end
POST /api/correction/{tool_name}
```

#### Long-Session Test (`tests/test_long_session.py`)
```python
# Validations
- NPC recall across multiple sessions
- Summary handling without context overflow
- Context assembler stability over 50+ turns
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
POST /world/create            # Initial chat-based world generation
POST /world/chat              # Ongoing interactive world refinement
POST /world/validate          # World structure validation
POST /api/sessions            # Create session
POST /api/sessions/{session_id}/start   # Start session (timestamp tracking)
POST /api/sessions/{session_id}/end     # End session (timestamp tracking)
POST /api/correction/{tool_name}        # Invoke whitelisted correction tool
GET  /                        # Serves the main HTML frontend
GET  /world/form              # World form editor page
GET  /character/create        # Character creator page
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

# Save methods for campaign initialization
DatabaseManager.save_character(character: Character) -> None
DatabaseManager.save_location(location: Location) -> None
DatabaseManager.save_item(item: Item) -> None
DatabaseManager.save_faction(faction: Faction) -> None
DatabaseManager.save_ability(ability: Ability) -> None
DatabaseManager.save_session(session_entity: Session) -> None

# Session lifecycle
DatabaseManager.start_session(session_id: uuid.UUID) -> bool
DatabaseManager.end_session(session_id: uuid.UUID) -> bool
DatabaseManager.get_active_sessions() -> List[Session]
DatabaseManager.get_session_by_id(session_id: uuid.UUID) -> Optional[Session]

# Event logging & state restoration
DatabaseManager.log_event(event_log) -> None
DatabaseManager.get_events_for_session(session_id) -> List[EventLog]
DatabaseManager.delete_events_for_session(session_id) -> None

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

### WorldCreationAPI (`app/api/world_creation.py`)
```python
WorldCreationAPI.create_world(request: Request)              # POST /world/create
WorldCreationAPI.chat_with_world_builder(request: Request)   # POST /world/chat
WorldCreationAPI.validate_world_structure(request: Request)  # POST /world/validate
```

### World Model (`app/models/world_models.py`)
```python
# Renamed from World to WorldTemplate to avoid conflict with the SQLModel World entity
WorldTemplate(name, description, tone, factions, locations, characters, abilities, rules)
WorldTemplate.to_dict()
WorldTemplate.from_dict()
WORLD_SCHEMA   # JSON schema for world structure validation
```

### Seed Script (`seed_dp.py`)
```python
# Creates tables and populates initial database content via SqlModel ORM
```

### Database Model Tests (`tests/test_database_models.py`)
```python
# Comprehensive test suite for all database models (imports, instantiation, datetime handling) — all passing
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

### Campaign Initializer (`app/engine/campaign_initializer.py`)
```python
class CampaignInitializer:
    def __init__(db_manager):
        # Initialize with database manager
    
    async def initialize_campaign_from_world(world_template, campaign_name, campaign_description, player_character_data):
        # Create campaign and instantiate all entities from world template
    
    async def create_character(campaign_id, character_data):
        # Create a new character in the campaign
    
    async def create_initial_session(campaign_id):
        # Create an initial session for the campaign

def initialize_campaign_from_world_template(db_manager, world_template, campaign_name, campaign_description, player_character_data):
    # Convenience function to initialize a campaign from a world template
```

This documentation reflects the current state of the KrckRP codebase, covering all implemented engine components, API surfaces, and integration points while maintaining alignment with the requirements specified in KrckRP-Requirements.md.