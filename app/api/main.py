"""
FastAPI application for KrckRP with KoboldCpp integration.
Handles game turns and streaming responses via SSE.
"""

from fastapi import FastAPI, HTTPException, Request, APIRouter
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
from app.models.database_models import GameTurn, DatabaseManager, Campaign, Character, Location, Item, Quest, Session, engine
from app.models.world_models import WorldTemplate
from app.engine.state_manager import StateManager
from app.engine.correction_assistant import CorrectionAssistant, CorrectionAssistantAPI
from app.api.world_creation import init_world_creation_api
import logging

# Initialize FastAPI app
app = FastAPI(title="KrckRP API", version="0.1.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create API router for prefixed endpoints
api_router = APIRouter(prefix="/api")

# Global clients for LLM services
kobold_client: KoboldCppClient = None
extractor: Extractor = None
state_manager: StateManager = None
correction_assistant: CorrectionAssistant = None
correction_assistant_api: CorrectionAssistantAPI = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown logic"""
    global kobold_client, extractor, state_manager, correction_assistant, correction_assistant_api
    
    # Initialize components on startup
    try:
        kobold_client = KoboldCppClient()
        extractor = Extractor()
        state_manager = StateManager()  # Use default db manager
        correction_assistant = CorrectionAssistant()
        correction_assistant_api = CorrectionAssistantAPI(correction_assistant)
        
        logger.info("FastAPI app initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize FastAPI components: {e}")
        raise

app.router.lifespan_context = lifespan

# Initialize world creation API endpoints
init_world_creation_api(app)

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

# Session Management Endpoints
@app.post("/api/sessions")
async def create_session(session_data: dict):
    """
    Create a new session.
    
    Args:
        session_data (dict): Data for the new session including campaign_id, name, description
        
    Returns:
        Dict with session details
    """
    try:
        db_manager = DatabaseManager()
        session_model = Session(
            id=uuid.uuid4(),
            campaign_id=session_data["campaign_id"],
            name=session_data["name"],
            description=session_data["description"]
        )
        await db_manager.save_session(session_model)
        
        return {
            "id": str(session_model.id),
            "campaign_id": str(session_model.campaign_id),
            "name": session_model.name,
            "description": session_model.description
        }
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/start")
async def start_session(session_id: str):
    """
    Mark a session as started.
    
    Args:
        session_id (str): ID of the session to start
        
    Returns:
        Dict with status
    """
    try:
        db_manager = DatabaseManager()
        success = await db_manager.start_session(uuid.UUID(session_id))
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "started", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/end")
async def end_session(session_id: str):
    """
    Mark a session as ended.
    
    Args:
        session_id (str): ID of the session to end
        
    Returns:
        Dict with status
    """
    try:
        db_manager = DatabaseManager()
        success = await db_manager.end_session(uuid.UUID(session_id))
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"status": "ended", "session_id": session_id}
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Correction Assistant Endpoints
@app.post("/api/correction/{tool_name}")
async def execute_correction_tool(tool_name: str, request: Request):
    """
    Execute a correction tool via the assistant API.
    
    Args:
        tool_name (str): Name of the tool to execute
        
    Returns:
        Dict with result details
    """
    try:
        # Get request data
        body = await request.json()
        
        # Execute the tool through the assistant API
        result = await correction_assistant_api.execute_tool(tool_name, **body)
        
        return result
    except Exception as e:
        logger.error(f"Error executing correction tool {tool_name}: {e}")
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
        
        # Use KoboldCpp to generate narrative text (streaming) 
        stream_generator = kobold_client.generate_narrative(turn_data)
        
        async def event_stream() -> AsyncGenerator[str, None]:
            """Generate Server-Sent Events for streaming."""
            try:
                full_narration = ""
                
                # Stream the narration
                async for chunk in stream_generator:
                    if chunk:
                        full_narration += chunk
                        yield f"data: {json.dumps({'type': 'narration', 'content': chunk})}\n\n"
                        
                # Extract structured data after narrative completion  
                extracted_data = await extractor.extract_structured_data(full_narration, turn_data)
                
                # Yield extraction results 
                yield f"data: {json.dumps({'type': 'extraction', 'data': extracted_data})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream_turn: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(event_stream(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"Error in streaming turn: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add static file serving for the manual data editor
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("app/static/index.html")

@app.get("/manual-editor")
async def read_manual_editor():
    """Serve the Manual Data Editor page"""
    return FileResponse("app/static/manual_data_editor.html")

# Add health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dict with status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Campaign endpoints (add missing campaign routes)
@api_router.get("/campaigns")
def list_campaigns():
    from sqlmodel import Session, select
    with Session(engine) as session:
        campaigns = session.exec(select(Campaign)).all()
        return campaigns

@api_router.post("/campaigns")
def create_campaign(campaign_data: dict):
    from sqlmodel import Session
    with Session(engine) as session:
        campaign = Campaign(**campaign_data)
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        return campaign

# Include the API router in the main app
app.include_router(api_router)