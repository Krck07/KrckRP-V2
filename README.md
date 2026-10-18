# KrckRP - AI RPG Engine

A local web-based RPG engine that combines narrative generation, game state management, and interactive storytelling using a local LLM.

## Features

- Campaign management with save/load functionality
- Real-time chat interface for player interaction  
- Persistent sidebar showing character stats, inventory, location, etc.
- Server-Sent Events (SSE) for streaming narrative updates
- Local AI integration via KoboldCpp

## Project Structure

```
app/
├── api/          # FastAPI endpoints
├── models/       # Database models and managers  
├── engine/       # Game state management
├── llm/          # LLM integration modules
├── static/       # Frontend assets (HTML, CSS, JS)
└── tests/        # Test suite
```

## Getting Started

1. Start the FastAPI server:
```bash
uvicorn app.api.main:app --reload
```

2. Access the frontend at `http://localhost:8000`

3. Create a campaign and start playing!

## Frontend Components

- **Campaign Selection Screen**: Choose existing campaigns or create new ones
- **Main Game UI**:
  - Persistent sidebar with character state (stats, inventory, location)
  - Real-time chat pane showing narrative updates from SSE
  - Text input for player commands/actions

## API Endpoints

### Campaign Management
- `GET /campaigns` - List all campaigns  
- `POST /campaigns` - Create a new campaign
- `GET /campaign/{id}/state` - Get current campaign state for UI

### Game Interaction
- `POST /turn` - Process a game turn (narration + extraction)
- `GET /turn/stream` - Stream narrative updates via SSE 
- `GET /health` - Health check endpoint

## Implementation Details  

This implementation includes:
1. Complete HTML/CSS/JS frontend with responsive design  
2. Campaign management endpoints for save/load functionality
3. Persistent sidebar displaying campaign state
4. Real-time streaming of game events through Server-Sent Events (SSE)
5. Proper API structure to support the UI components

## Requirements  

- Python 3.8+
- FastAPI 
- SQLModel with SQLite backend
- KoboldCpp running locally for LLM functionality