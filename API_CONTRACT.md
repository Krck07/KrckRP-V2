# KrckRP API Contract

## Overview

This document defines all public endpoints for communication between frontend and backend, including request/response formats.

## Backend Endpoints

### Authentication & Session Management

#### POST `/api/auth/login`
- **Description**: Authenticate user session (currently unused in local version)
- **Request Body**: 
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "token": "string",
    "user_id": "string"
  }
  ```

#### GET `/api/session/status`
- **Description**: Check current session status
- **Response**:
  ```json
  {
    "authenticated": true,
    "session_id": "string",
    "active_campaign": "string"
  }
  ```

### World & Campaign Management

#### GET `/api/worlds`
- **Description**: List all available worlds
- **Response**:
  ```json
  [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "created_at": "datetime"
    }
  ]
  ```

#### GET `/api/worlds/{world_id}`
- **Description**: Get world details
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "ruleset": "object"
  }
  ```

#### POST `/api/campaigns`
- **Description**: Create new campaign from a world template
- **Request Body**:
  ```json
  {
    "world_id": "string",
    "name": "string"
  }
  ```
- **Response**:
  ```json
  {
    "id": "string",
    "world_id": "string",
    "name": "string"
  }
  ```

#### GET `/api/campaigns/{campaign_id}`
- **Description**: Get campaign details
- **Response**:
  ```json
  {
    "id": "string",
    "world_id": "string", 
    "name": "string",
    "created_at": "datetime"
  }
  ```

### Character Management

#### GET `/api/characters/me`
- **Description**: Get current player character details  
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string",
    "stats": {"stat_name": int},
    "inventory": ["item_id"],
    "location_id": "string"
  }
  ```

#### PUT `/api/characters/me`
- **Description**: Update character details
- **Request Body**:
  ```json
  {
    "name": "string",
    "stats": {"stat_name": int}
  }
  ```
- **Response**: Updated character object

### Location Management

#### GET `/api/locations/{location_id}`
- **Description**: Get location details
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string", 
    "description": "string",
    "connections": [{"destination_id": "string", "distance": int}],
    "characters_present": ["character_id"],
    "items": ["item_id"]
  }
  ```

#### GET `/api/locations/current`
- **Description**: Get current location details
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "connections": [{"destination_id": "string", "distance": int}],
    "characters_present": ["character_id"],
    "items": ["item_id"]
  }
  ```

### Action Processing

#### POST `/api/actions`
- **Description**: Process player action
- **Request Body**:
  ```json
  {
    "action_text": "string",
    "context_override": "object" // Optional override for narrative context 
  }
  ```
- **Response (Streaming)**: Server-Sent Events with stream of updates

#### GET `/api/turns/{turn_id}/events`
- **Description**: Get events from a specific turn
- **Response**:
  ```json
  [
    {
      "id": "string",
      "type": "engine|extractor|player_correction|assistant_correction|world_creation",
      "description": "string",
      "timestamp": "datetime"
    }
  ]
  ```

### Memory & Context

#### POST `/api/context`
- **Description**: Retrieve context for narrator prompt
- **Request Body**:
  ```json
  {
    "turn_id": "string" 
  }
  ```
- **Response**:
  ```json
  {
    "world_rules": "object",
    "current_location": "object",
    "player_character": "object",
    "nearby_characters": ["object"],
    "active_quests": ["object"],
    "recent_events": ["object"],
    "relevant_memories": ["string"]
  }
  ```

#### POST `/api/search`
- **Description**: Search episodic memories  
- **Request Body**:
  ```json
  {
    "query": "string",
    "limit": int,
    "filters": {"character_id": "string"}
  }
  ```
- **Response**:
  ```json
  [
    {
      "id": "string",
      "content": "string", 
      "metadata": {"turn_id": "string"},
      "similarity_score": float
    }
  ]
  ```

### Event Management

#### GET `/api/events`
- **Description**: Get recent events from campaign
- **Response**:
  ```json
  [
    {
      "id": "string",
      "type": "engine|extractor|player_correction|assistant_correction|world_creation",
      "description": "string", 
      "timestamp": "datetime",
      "source_turn_id": "string"
    }
  ]
  ```

#### POST `/api/events/undo`
- **Description**: Undo to a specific turn
- **Request Body**:
  ```json
  {
    "turn_id": "string"
  }
  ```
- **Response**: Success confirmation

## Frontend Endpoints

### Streamed Responses (Server-Sent Events)

#### GET `/api/stream/{session_id}`  
- **Description**: Stream narration updates for a session
- **Headers**: `Content-Type: text/event-stream`
- **Events**:
  - `turn_start`: {"turn_id": "string"}
  - `narration_chunk`: {"text": "string"} 
  - `turn_complete`: {"events": ["object"]}

### Session Management

#### POST `/api/session/start/{campaign_id}`
- **Description**: Start new session for campaign
- **Response**:
  ```json
  {
    "session_id": "string",
    "current_turn_id": "string"
  }
  ```

## SSE Event Format

All streaming endpoints use Server-Sent Events with the following structure:

```text
event: event_name
data: {"key": "value", ...}
```

### Available Events:
- `turn_start` - Start of a new turn processing
- `narration_chunk` - Chunk of narrative text (streamed)
- `turn_complete` - Turn completed with events 
- `error` - Error occurred during processing

## Data Models

### Character
```json
{
  "id": "string",
  "name": "string", 
  "description": "string",
  "stats": {"stat_name": int},
  "inventory": ["item_id"],
  "location_id": "string"
}
```

### Location  
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "connections": [{"destination_id": "string", "distance": int}],
  "characters_present": ["character_id"],
  "items": ["item_id"]
}
```

### Turn
```json
{
  "id": "string", 
  "input_text": "string",
  "narration": "string",
  "events": ["event_id"]
}
```