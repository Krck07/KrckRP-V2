"""
FastAPI application for KrckRP with KoboldCpp integration.
Handles game turns and streaming responses via SSE.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator
from contextlib import asynccontextmanager

# Import our custom modules
from app.llm.kobold_cpp_client import KoboldCppClient
from app.llm.extractor import Extractor
from app.models.database_models import GameTurn, DatabaseManager
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)