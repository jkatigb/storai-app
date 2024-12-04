from fastapi import FastAPI, HTTPException
from langchain.chat_models import ChatOpenAI
from .models import StoryParameters, Story, StorySection, Scene
from .graph import create_story_graph, create_initial_state
import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

app = FastAPI(title="Children's Story Generator", description="An AI-powered children's story generation service")

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-4",  # Using GPT-4 for better story generation
    temperature=0.7
)

# Initialize story graph
story_graph = create_story_graph(llm)

# Store active story sessions
story_sessions: Dict[str, Dict] = {}

@app.post("/story/start")
async def start_story(parameters: StoryParameters):
    """Start a new story generation session."""
    try:
        # Create initial state
        initial_state = create_initial_state(parameters)
        
        # Run the first step (synopsis generation)
        result = await story_graph.arun(initial_state)
        
        # Generate session ID (you might want to use a proper UUID)
        session_id = str(len(story_sessions) + 1)
        story_sessions[session_id] = result
        
        return {
            "session_id": session_id,
            "current_step": result["current_step"],
            "story": result["story"],
            "requires_feedback": result["current_step"].startswith("review_")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/story/{session_id}/feedback")
async def provide_feedback(
    session_id: str,
    feedback: str,
    approved: bool
):
    """Provide feedback for the current step of story generation."""
    try:
        if session_id not in story_sessions:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        # Update state with feedback
        state = story_sessions[session_id]
        state["user_feedback"] = feedback
        state["approved"] = approved
        
        # Run next step
        result = await story_graph.arun(state)
        story_sessions[session_id] = result
        
        return {
            "current_step": result["current_step"],
            "story": result["story"],
            "requires_feedback": result["current_step"].startswith("review_"),
            "complete": result["current_step"] == "complete"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/story/{session_id}/status")
async def get_story_status(session_id: str):
    """Get the current status of a story generation session."""
    try:
        if session_id not in story_sessions:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        state = story_sessions[session_id]
        return {
            "current_step": state["current_step"],
            "story": state["story"],
            "requires_feedback": state["current_step"].startswith("review_"),
            "complete": state["current_step"] == "complete"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/story/{session_id}/preview")
async def get_story_preview(session_id: str):
    """Get a preview of the story in its current state."""
    try:
        if session_id not in story_sessions:
            raise HTTPException(status_code=404, detail="Story session not found")
        
        story = story_sessions[session_id]["story"]
        
        # Format story for preview
        preview = {
            "title": story.title,
            "synopsis": story.synopsis,
            "sections": [
                {
                    "name": section.name,
                    "scenes": [
                        {
                            "text": scene.text,
                            "image_url": scene.image_url
                        }
                        for scene in section.scenes
                    ]
                }
                for section in story.sections
            ]
        }
        
        return preview
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 