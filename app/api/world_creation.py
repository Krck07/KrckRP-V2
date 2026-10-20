"""
World Creation API module for KrckRP.
Handles AI-powered world building through chat-based interaction with structured extraction.
"""

from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Any, List
import json
import logging

logger = logging.getLogger(__name__)

# Import our custom modules
from app.llm.kobold_cpp_client import KoboldCppClient
from app.llm.extractor import Extractor
from app.models.database_models import DatabaseManager, Campaign
from app.engine.state_manager import StateManager
from app.models.world_models import WorldTemplate


logger = logging.getLogger(__name__)

# Global clients for LLM services (these should be managed by lifespan in main.py)
kobold_client: KoboldCppClient = None
extractor: Extractor = None

class WorldCreationAPI:
    """Handles world creation functionality via chat and structured extraction."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup the API routes for world creation"""
        @self.app.post("/world/create")
        async def create_world(request: Request):
            """
            Create a new world through AI-powered chat interaction.
            
            This endpoint accepts user input about desired world characteristics
            and uses an LLM to generate structured world data using the Extractor pattern.
            
            The flow is:
            1. User provides initial world concept
            2. AI generates narrative description of proposed world elements  
            3. Extractor converts narrative into structured JSON format
            4. Structured data is validated and stored as a new World template
            
            Returns:
                Dict containing the created world's metadata and ID
            """
            try:
                # Get input from request
                body = await request.json()
                
                # Process with state manager to prepare context
                turn_data = await StateManager().prepare_turn(body)
                
                # Use KoboldCpp to generate initial world description narrative
                stream_generator = kobold_client.generate_narrative(turn_data)
                
                # Collect all streamed content
                full_narration = ""
                async for chunk in stream_generator:
                    full_narration += chunk
                
                # Extract structured data using the extractor 
                extracted_data = await extractor.extract_structured_data(full_narration, turn_data)
                
                # Validate and create world from extraction results
                world_data = self._validate_and_create_world(extracted_data["data"])
                
                # Save to database as a new world template
                db_manager = DatabaseManager()
                world_id = db_manager.create_world(world_data)
                
                return {
                    "status": "success",
                    "world_id": str(world_id),
                    "message": "World created successfully"
                }
                
            except Exception as e:
                logger.error(f"Error creating world: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/world/chat")
        async def chat_with_world_builder(request: Request):
            """
            Chat endpoint for interactive world building.
            
            Allows users to have a conversation with the AI about world details,
            generating structured output using Extractor pattern at each step.
            
            Returns:
                Dict containing the generated response and extracted data
            """
            try:
                body = await request.json()
                
                # Process the chat input through state manager  
                turn_data = await StateManager().prepare_turn(body)
                
                # Generate narrative response from AI
                stream_generator = kobold_client.generate_narrative(turn_data)
                
                # Collect all streamed content
                full_response = ""
                async for chunk in stream_generator:
                    full_response += chunk
                
                # Extract structured data from the chat response 
                extracted_data = await extractor.extract_structured_data(full_response, turn_data)
                
                return {
                    "response": full_response,
                    "extraction": extracted_data,
                    "source": "world_creation"
                }
                
            except Exception as e:
                logger.error(f"Error in world chat: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/world/validate")
        async def validate_world_structure(request: Request):
            """
            Validate a proposed world structure and extract it into standard format.
            
            This endpoint can be used to directly submit a JSON world definition
            for validation against our world schema.
            
            Returns:
                Dict containing validation results and normalized data
            """
            try:
                body = await request.json()
                
                # Validate the submitted world definition  
                validated_data = self._validate_world_structure(body)
                
                return {
                    "status": "valid",
                    "data": validated_data,
                    "message": "World structure is valid"
                }
                
            except Exception as e:
                logger.error(f"Error validating world: {e}")
                raise HTTPException(status_code=400, detail=str(e))
    
    def _validate_and_create_world(self, extracted_world_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize the extracted world data into standard format.
        
        Args:
            extracted_world_data (Dict): Raw extracted world data from AI
            
        Returns:
            Dict: Normalized world definition ready for storage
        """
        # Apply validation rules to make sure required fields are present
        normalized = {
            "name": extracted_world_data.get("world_name", "Unnamed World"),
            "description": extracted_world_data.get("world_description", ""),
            "tone": extracted_world_data.get("tone", {}),
            "factions": extracted_world_data.get("factions", []),
            "locations": extracted_world_data.get("locations", []),
            "characters": extracted_world_data.get("characters", []),
            "abilities": extracted_world_data.get("ability_groups", []),
            "rules": extracted_world_data.get("world_rules", {})
        }
        
        # Ensure all required fields are properly structured
        if not normalized["name"]:
            raise ValueError("World must have a name")
            
        return normalized
    
    def _validate_world_structure(self, world_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the structure of a complete world definition.
        
        Args:
            world_json (Dict): Full JSON representation of world
            
        Returns:
            Dict: Validated and normalized world data
        """
        # Basic validation checks for required fields  
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in world_json:
                raise ValueError(f"World definition missing required field: {field}")
                
        return world_json

# Initialize the WorldCreationAPI when this module is imported
world_creation_api = None

def init_world_creation_api(app: FastAPI):
    """Initialize the world creation API endpoints"""
    global world_creation_api
    if world_creation_api is None:
        world_creation_api = WorldCreationAPI(app)
    
    return world_creation_api