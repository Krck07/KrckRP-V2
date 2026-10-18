"""
FastAPI application for KrckRP with KoboldCpp integration.
Handles game turns and streaming responses via SSE.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
from typing import AsyncGenerator, List, Optional
from contextlib import asynccontextmanager
import uuid

# Import our custom modules
from app.llm.kobold_cpp_client import KoboldCppClient
from app.llm.extractor import Extractor
from app.models.database_models import GameTurn, DatabaseManager, Campaign, Character, Location, Item, Quest
from app.engine.state_manager import StateManager
import logging

# Initialize FastAPI app
app = FastAPI(title="KrckRP API", version="0.1.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global clients for LLM services
kobold_client: KoboldCppClient = None
extractor: Extractor = None
state_manager: StateManager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic"""
    global kobold_client, extractor, state_manager
    
    # Initialize components on startup
    try:
        kobold_client = KoboldCppClient()
        extractor = Extractor()
        state_manager = StateManager()  # Use default db manager
        
        logger.info("FastAPI app initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize FastAPI components: {e}")
        raise

app.router.lifespan_context = lifespan

@app.post("/turn")
async def handle_turn(request: Request):
    """
    Handle a game turn with streaming narration and synchronous extraction.
    
    This endpoint processes the turn, streams narrative text using KoboldCpp,
    waits for the narrator to complete, then uses the extractor to get structured data.
    State changes are only committed after successful completion of both steps.
    """
    try:
        # Get input from request
        body = await request.json()
        
        # Process with state manager (this will validate and prepare game state)
        turn_data = await state_manager.prepare_turn(body)
        
        # Use KoboldCpp to generate narrative text (streaming)
        stream_generator = kobold_client.generate_narrative(turn_data)
        
        # Collect all streamed content
        full_narration = ""
        async for chunk in stream_generator:
            full_narration += chunk
        
        # Extract structured data using the extractor 
        extracted_data = await extractor.extract_structured_data(full_narration, turn_data)
        
        # Commit state changes only after successful narration and extraction
        result = await state_manager.commit_turn(turn_data, extracted_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/turn/stream")
async def stream_turn(request: Request):
    """
    Streaming endpoint for game turns using Server-Sent Events.
    This provides real-time updates during the narrative generation process.
    """
    try:
        body = await request.json()
        
        # Process with state manager
        turn_data = await state_manager.prepare_turn(body)
        
        async def event_generator():
            """Generate events for streaming response"""
            # Stream narrative text
            stream_generator = kobold_client.generate_narrative(turn_data)
            
            full_narration = ""
            async for chunk in stream_generator:
                full_narration += chunk
                
                # Send each chunk as an event
                yield f"data: {json.dumps({'type': 'narration', 'chunk': chunk})}\n\n"
                
                # Add delay to simulate real streaming
                await asyncio.sleep(0.01)
            
            # Extract structured data after narration completes
            extracted_data = await extractor.extract_structured_data(full_narration, turn_data)
            
            # Send the final extraction result
            yield f"data: {json.dumps({'type': 'extraction', 'data': extracted_data})}\n\n"
            
            # Commit state changes only after successful completion
            result = await state_manager.commit_turn(turn_data, extracted_data)  
            yield f"data: {json.dumps({'type': 'commit', 'result': result})}\n\n"
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error streaming turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test if KoboldCpp is reachable
        is_kobold_healthy = await kobold_client.is_healthy()
        
        return {
            "status": "healthy",
            "kobold_cpp": is_kobold_healthy,
            "timestamp": asyncio.get_event_loop().time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# Campaign management endpoints
@app.get("/campaigns")
async def list_campaigns():
    """Get all campaigns"""
    try:
        db_manager = DatabaseManager()
        campaigns = db_manager.get_all_campaigns()
        return campaigns
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns")
async def create_campaign(campaign_data: dict):
    """Create a new campaign"""
    try:
        db_manager = DatabaseManager()
        campaign_id = db_manager.create_campaign(
            name=campaign_data.get('name'),
            description=campaign_data.get('description', '')
        )
        
        # Return the created campaign
        campaign = db_manager.get_campaign(campaign_id)
        return campaign
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaign/{campaign_id}/state")
async def get_campaign_state(campaign_id: str):
    """Get the current state of a campaign for UI display"""
    try:
        db_manager = DatabaseManager()
        
        # Get basic campaign info
        campaign = db_manager.get_campaign(uuid.UUID(campaign_id))
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get character and location (assuming player character is the first one)
        characters = db_manager.get_characters_by_campaign(uuid.UUID(campaign_id))
        locations = db_manager.get_locations_by_campaign(uuid.UUID(campaign_id))
        items = db_manager.get_items_by_campaign(uuid.UUID(campaign_id))
        quests = db_manager.get_quests_by_campaign(uuid.UUID(campaign_id))
        
        # Get stats - we'll use a simplified example
        stats = {
            "strength": 10,
            "dexterity": 12,
            "constitution": 8,
            "intelligence": 14,
            "wisdom": 13,
            "charisma": 9
        }
        
        # Get the current location (simplified)
        location = locations[0] if locations else None
        
        return {
            "name": campaign.name,
            "stats": stats,
            "inventory": [
                {"name": item.name, "description": item.description}
                for item in items
            ],
            "location": {
                "name": location.name if location else "Unknown Location",
                "description": location.description if location else ""
            } if location or locations else None,
            "characters": [
                {"name": char.name, "description": char.description}
                for char in characters
            ],
            "quests": [
                {"name": quest.name, "description": quest.description}
                for quest in quests
            ]
        }
    except Exception as e:
        logger.error(f"Error getting campaign state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/state")
async def get_debug_state(campaign_id: str):
    """
    Debug endpoint showing the fully assembled prompt sent to the Narrator,
    the raw JSON returned by the Extractor, and any proposals rejected by validator.
    
    This endpoint is hidden from normal UI access but available for developers
    during development.
    
    Args:
        campaign_id (str): The ID of the campaign to debug
        
    Returns:
        Dict: Debug information including prompts, extractions and rejections
    """
    try:
        db_manager = DatabaseManager()
        
        # Get recent turns with their details
        recent_turns = await db_manager.get_recent_turns_with_details(uuid.UUID(campaign_id), 5)
        
        debug_data = {
            "campaign_id": campaign_id,
            "last_turns": [
                {
                    "turn_id": turn["turn_id"],
                    "prompt": turn["prompt"],
                    "timestamp": turn["timestamp"]
                }
                for turn in recent_turns
            ],
            "extractor_results": [
                {
                    "turn_id": turn["turn_id"],
                    "extraction_data": turn["extraction_data"]
                }
                for turn in recent_turns
            ],
            "rejected_proposals": []  # In a real implementation this would come from validation/rejection logic
        }
        
        return debug_data
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)