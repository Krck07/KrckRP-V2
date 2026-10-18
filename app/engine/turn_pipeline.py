"""
Turn Pipeline Orchestrator for KrckRP engine.
Orchestrates the turn processing pipeline including intent interpretation,
mechanics resolution, context assembly, narration, and data extraction.
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import logging

# Import database models
from app.models.database_models import GameTurn, DatabaseManager
from app.llm.extractor import Extractor
import uuid

logger = logging.getLogger(__name__)

class Outcome:
    """
    Represents the outcome of an action resolution.
    
    This is a placeholder that will be expanded in future sessions to include
    detailed game state changes and effects.
    """
    def __init__(self, success: bool = True, message: str = "", data: Dict[str, Any] = None):
        self.success = success
        self.message = message
        self.data = data or {}

class TurnPipeline:
    """
    Orchestrates the turn processing pipeline for KrckRP.
    
    Pipeline flow:
    Interpret Intent -> Resolve Mechanics (stub) -> Assemble Context (stub) 
    -> Narrate -> Extract
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the turn pipeline orchestrator."""
        self.db_manager = db_manager or DatabaseManager()
        self.extractor = Extractor()
        
    async def process_turn(self, raw_input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a complete game turn through the pipeline.
        
        Args:
            raw_input_data (Dict): Raw input data for the turn
            
        Returns:
            Dict: Final processed result including narrative and extracted data
        """
        # Step 1: Interpret Intent
        intent = self._interpret_intent(raw_input_data)
        logger.info(f"Interpreted intent: {intent}")
        
        # Step 2: Resolve Mechanics (stub implementation)
        outcome = self._resolve_mechanics(intent)
        logger.info(f"Resolved mechanics with outcome: {outcome.message}")
        
        # Step 3: Assemble Context (stub implementation)  
        context_prompt = await self._assemble_context(intent, outcome, raw_input_data.get('session_id'))
        logger.info("Assembled context prompt")
        
        # Step 4: Narrate
        narrative_text = await self._narrate(context_prompt)
        logger.info("Generated narrative")
        
        # Step 5: Extract structured data from narrative
        extracted_data = await self._extract(narrative_text, raw_input_data)
        logger.info("Extracted structured data")
        
        return {
            "narrative": narrative_text,
            "extracted_data": extracted_data,
            "intent": intent,
            "outcome": outcome
        }
    
    def _interpret_intent(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret the raw player input to determine game intent.
        
        This is a simple stub that would be enhanced with NLP capabilities later.
        
        Args:
            input_data (Dict): Raw player input
            
        Returns:
            Dict: Interpreted intent data
        """
        return {
            "action": input_data.get("prompt", "").split()[0] if input_data.get("prompt") else "unknown",
            "target": input_data.get("target", None),
            "intent_text": input_data.get("prompt", ""),
            "context": input_data.get("context", {})
        }
    
    def _resolve_mechanics(self, intent: Dict[str, Any]) -> Outcome:
        """
        Stub implementation for resolving game mechanics based on intent.
        
        This will be expanded in later sessions to include proper resolution logic
        with dice rolls, stat checks, etc.
        
        Args:
            intent (Dict): Interpreted player intent
            
        Returns:
            Outcome: Result of the action resolution
        """
        # Stub implementation - would contain actual game mechanics
        return Outcome(
            success=True,
            message=f"Action '{intent['action']}' resolved successfully",
            data={"resolved_action": intent["action"]}
        )
    
    async def _assemble_context(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Assemble contextual information from multiple sources with strict token budgets.
        
        Combines SQL state, active quests, rolling summaries, recent raw turns,
        and retrieved vector memories into a single prompt string.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID for filtering NPCs
            
        Returns:
            str: Contextual prompt string for narrative generation
        """
        # Initialize token budget for each section
        remaining_tokens = 2048  # Total token budget - adjust as needed
        context_parts = []
        
        # Section 1: Current SQL State (600 tokens max)
        sql_state_section = await self._get_sql_state(intent, outcome, session_id)
        if sql_state_section:
            section_tokens = len(sql_state_section.split())  # Approximate token count
            if section_tokens <= 600:
                context_parts.append(f"SQL State:\n{sql_state_section}")
                remaining_tokens -= section_tokens
            else:
                # Truncate if necessary (simplified truncation)
                truncated = " ".join(sql_state_section.split()[:600])
                context_parts.append(f"SQL State:\n{truncated}")
                remaining_tokens -= 600
        
        # Section 2: Active Quests (400 tokens max)
        active_quests_section = await self._get_active_quests(intent, outcome, session_id)
        if active_quests_section:
            section_tokens = len(active_quests_section.split())
            if section_tokens <= 400 and remaining_tokens >= section_tokens:
                context_parts.append(f"Active Quests:\n{active_quests_section}")
                remaining_tokens -= section_tokens
            elif section_tokens > 400:
                truncated = " ".join(active_quests_section.split()[:400])
                context_parts.append(f"Active Quests:\n{truncated}")
                remaining_tokens -= 400
        
        # Section 3: Rolling Summary (400 tokens max)
        rolling_summary_section = await self._get_rolling_summary(intent, outcome, session_id)
        if rolling_summary_section:
            section_tokens = len(rolling_summary_section.split())
            if section_tokens <= 400 and remaining_tokens >= section_tokens:
                context_parts.append(f"Rolling Summary:\n{rolling_summary_section}")
                remaining_tokens -= section_tokens
            elif section_tokens > 400:
                truncated = " ".join(rolling_summary_section.split()[:400])
                context_parts.append(f"Rolling Summary:\n{truncated}")
                remaining_tokens -= 400
        
        # Section 4: Recent Raw Turns (300 tokens max)
        recent_turns_section = await self._get_recent_raw_turns(intent, outcome, session_id)
        if recent_turns_section:
            section_tokens = len(recent_turns_section.split())
            if section_tokens <= 300 and remaining_tokens >= section_tokens:
                context_parts.append(f"Recent Turns:\n{recent_turns_section}")
                remaining_tokens -= section_tokens
            elif section_tokens > 300:
                truncated = " ".join(recent_turns_section.split()[:300])
                context_parts.append(f"Recent Turns:\n{truncated}")
                remaining_tokens -= 300
        
        # Section 5: Retrieved Vector Memories (348 tokens max - remainder)
        vector_memories_section = await self._get_vector_memories(intent, outcome, session_id)
        if vector_memories_section:
            section_tokens = len(vector_memories_section.split())
            if section_tokens <= remaining_tokens and remaining_tokens > 0:
                context_parts.append(f"Vector Memories:\n{vector_memories_section}")
            elif remaining_tokens > 0:
                truncated = " ".join(vector_memories_section.split()[:remaining_tokens])
                context_parts.append(f"Vector Memories:\n{truncated}")
        
        # Combine all sections
        return "\n\n".join(context_parts) if context_parts else "No context available"
    
    async def _narrate(self, context_prompt: str) -> str:
        """
        Generate narrative text using the LLM.
        
        This method is a placeholder that would integrate with actual LLM services
        like KoboldCpp or mock implementations.
        
        Args:
            context_prompt (str): Prompt to use for narrative generation
            
        Returns:
            str: Generated narrative text
        """
        # Placeholder implementation - this would interface with the LLM service
        return f"Narrative generated based on context: {context_prompt}"

    async def _get_sql_state(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Get current SQL state information for the context.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID
            
        Returns:
            str: Formatted SQL state information
        """
        # For now, we'll get basic character info from the database
        try:
            # Extract campaign id and character info from intent or outcome
            campaign_id = intent.get('campaign_id')
            if not campaign_id:
                return "No campaign context available."
                
            # Get characters in campaign (simplified)
            characters = self.db_manager.get_characters_by_campaign(campaign_id)
            character_info = [f"{char.name}: {char.description}" for char in characters]
            
            # Get locations
            locations = self.db_manager.get_locations_by_campaign(campaign_id)
            location_info = [f"{loc.name}: {loc.description}" for loc in locations]
            
            return f"Characters: {', '.join(character_info)}\nLocations: {', '.join(location_info)}"
        except Exception as e:
            print(f"Error getting SQL state: {e}")
            return "SQL state information unavailable."

    async def _get_active_quests(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Get active quests for the campaign context.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID
            
        Returns:
            str: Formatted active quest information
        """
        try:
            campaign_id = intent.get('campaign_id')
            if not campaign_id:
                return "No campaign context available."
                
            # Get quests from database
            quests = await self.db_manager.get_quests_by_campaign(campaign_id)
            quest_info = [f"{quest.name}: {quest.description}" for quest in quests]
            
            return f"Active Quests: {', '.join(quest_info)}"
        except Exception as e:
            print(f"Error getting active quests: {e}")
            return "Quest information unavailable."

    async def _get_rolling_summary(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Get rolling summary of recent events for the campaign.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID
            
        Returns:
            str: Formatted rolling summary information
        """
        try:
            campaign_id = intent.get('campaign_id')
            if not campaign_id:
                return "No campaign context available."
                
            # Get the most recent summary for this campaign
            summary = await self.db_manager.get_summary_by_campaign(campaign_id)
            if summary and summary.content:
                return f"{summary.content}"
            else:
                return "No rolling summary available yet."
        except Exception as e:
            print(f"Error getting rolling summary: {e}")
            return "Rolling summary unavailable."

    async def _get_recent_raw_turns(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Get recent raw turns from the database.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID
            
        Returns:
            str: Formatted recent turn information
        """
        try:
            campaign_id = intent.get('campaign_id')
            if not campaign_id:
                return "No campaign context available."
                
            # Get the last few turns for context
            recent_turns = await self.db_manager.get_recent_turns(campaign_id, limit=3)
            turn_info = []
            for turn in recent_turns:
                if hasattr(turn, 'prompt') and turn.prompt:
                    turn_info.append(f"Turn {turn.turn_id}: {turn.prompt}")
                
            return "\n".join(turn_info) if turn_info else "No recent turns available."
        except Exception as e:
            print(f"Error getting recent turns: {e}")
            return "Recent turn information unavailable."

    async def _get_vector_memories(self, intent: Dict[str, Any], outcome: Outcome, session_id: uuid.UUID = None) -> str:
        """
        Get vector memories relevant to the context with NPC knowledge filter.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of mechanics resolution
            session_id (uuid.UUID): The current session ID
            
        Returns:
            str: Formatted vector memory information
        """
        try:
            from app.memory.semantic_memory import SemanticMemoryManager
            semantic_manager = SemanticMemoryManager(self.db_manager)
            
            # Get relevant memories using the intent as query
            if not intent.get("intent_text"):
                return "No context for memory search."
                
            # Search for similar content in vector store
            results = await semantic_manager.search_similar(intent["intent_text"], limit=5)
            
            filtered_memories = []
            if session_id:
                # Filter memories based on witness metadata - NPCs only know what they witnessed
                for result in results:
                    metadata = result.get("metadata", {})
                    # If there's no session ID or the session matches, include it
                    if not metadata.get("session_id") or str(metadata["session_id"]) == str(session_id):
                        filtered_memories.append(result["content"])
            else:
                # No session filtering, return all
                filtered_memories = [result["content"] for result in results]
            
            return "\n".join(filtered_memories) if filtered_memories else "No relevant memories found."
        except Exception as e:
            print(f"Error getting vector memories: {e}")
            return "Vector memory information unavailable."
    
    async def _extract(self, narrative_text: str, original_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from the narrative text using JSON grammar.
        
        This method specifically handles extracting known entity IDs and names
        to prevent resolution failures in the extraction process.
        
        Args:
            narrative_text (str): Narrative generated by LLM
            original_input (Dict): Original player input for reference
            
        Returns:
            Dict: Extracted structured data
        """
        # Create a payload that includes known entities from current scene
        entity_payload = self._prepare_entity_payload(original_input)
        
        # Pass the entity context to extractor so it can avoid resolution failures
        extraction_context = {
            "narrative": narrative_text,
            "entities": entity_payload
        }
        
        # Extract structured data using JSON schema - this will use the extractor's 
        # built-in capability for handling known entities
        return await self.extractor.extract_structured_data(narrative_text, extraction_context)
    
    def _prepare_entity_payload(self, original_input: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        """
        Prepare a payload with known entity IDs and names to prevent resolution failures.
        
        Args:
            original_input (Dict): Original player input containing scene context
            
        Returns:
            Dict: Payload containing lists of known entities
        """
        # Extract entity information from the original input or game state
        entities = []
        
        # Add character information if available
        characters = original_input.get("characters", [])
        char_entities = []
        for char in characters:
            if isinstance(char, dict) and "id" in char and "name" in char:
                char_entities.append({"id": char["id"], "name": char["name"]})
            elif isinstance(char, str):
                # If it's just a string name
                char_entities.append({"id": f"char_{len(char_entities)}", "name": char})
        
        # Add location information if available  
        locations = original_input.get("locations", [])
        loc_entities = []
        for loc in locations:
            if isinstance(loc, dict) and "id" in loc and "name" in loc:
                loc_entities.append({"id": loc["id"], "name": loc["name"]})
            elif isinstance(loc, str):
                # If it's just a string name
                loc_entities.append({"id": f"loc_{len(loc_entities)}", "name": loc})
        
        # Add item information if available
        items = original_input.get("items", [])
        item_entities = []
        for item in items:
            if isinstance(item, dict) and "id" in item and "name" in item:
                item_entities.append({"id": item["id"], "name": item["name"]})
            elif isinstance(item, str):
                # If it's just a string name
                item_entities.append({"id": f"item_{len(item_entities)}", "name": item})
        
        return {
            "characters": char_entities,
            "locations": loc_entities,
            "items": item_entities
        }

# Stub interfaces that will be implemented in future sessions
class ActionResolver(ABC):
    """Abstract interface for resolving actions."""
    
    @abstractmethod
    def resolve_action(self, intent: Dict[str, Any]) -> Outcome:
        """
        Resolve a player action based on game mechanics.
        
        Args:
            intent (Dict): Interpreted player intent
            
        Returns:
            Outcome: Result of the action resolution
        """
        pass

class ContextAssembler(ABC):
    """Abstract interface for assembling narrative context."""
    
    @abstractmethod  
    def assemble_context(self, intent: Dict[str, Any], outcome: Outcome) -> str:
        """
        Assemble contextual information for LLM prompt.
        
        Args:
            intent (Dict): Interpreted player intent
            outcome (Outcome): Result of action resolution
            
        Returns:
            str: Contextual prompt string
        """
        pass

# Utility function to convert Pydantic/JSON schema into GBNF grammar
def json_schema_to_gbnf(schema: Dict[str, Any], name: str = "schema") -> str:
    """
    Convert a JSON schema (Pydantic or plain) into GBNF grammar format for KoboldCpp.
    
    This utility helps bridge the gap between Python data models and LLM grammar requirements.
    
    Args:
        schema (Dict): JSON schema definition
        name (str): Name to use in the GBNF rule
        
    Returns:
        str: GBNF grammar string suitable for KoboldCpp
    """
    # Placeholder implementation - this would be more sophisticated in practice
    return f"""
{schema}
"""