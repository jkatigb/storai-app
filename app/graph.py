from typing import Dict, TypedDict, Annotated, List
from langgraph.graph import Graph, StateGraph
from langchain.chat_models import ChatOpenAI
from .models import Story, StoryParameters, StorySection, Scene

class StoryState(TypedDict):
    story: Story
    current_step: str
    user_feedback: str
    approved: bool

def create_synopsis(state: StoryState, llm: ChatOpenAI) -> StoryState:
    """Generate story synopsis based on parameters."""
    story = state["story"]
    story.synopsis = story.generate_synopsis()
    state["current_step"] = "review_synopsis"
    return state

def create_outline(state: StoryState, llm: ChatOpenAI) -> StoryState:
    """Generate story outline after synopsis is approved."""
    story = state["story"]
    story.sections = story.generate_outline()
    state["current_step"] = "review_outline"
    return state

def develop_section(state: StoryState, llm: ChatOpenAI) -> StoryState:
    """Develop the current section into detailed scenes."""
    story = state["story"]
    current_section = story.sections[story.current_section_index]
    current_section.scenes = current_section.develop_scenes()
    state["current_step"] = "review_section"
    return state

def generate_images(state: StoryState, llm: ChatOpenAI) -> StoryState:
    """Generate image prompts and images for the current section."""
    story = state["story"]
    current_section = story.sections[story.current_section_index]
    
    for scene in current_section.scenes:
        scene.image_prompt = scene.generate_image_prompt()
        # TODO: Implement actual image generation
        scene.image_url = ""  # Placeholder
    
    state["current_step"] = "review_images"
    return state

def process_feedback(state: StoryState) -> StoryState:
    """Process user feedback and update story state."""
    if state["approved"]:
        story = state["story"]
        current_step = state["current_step"]
        
        if current_step == "review_synopsis":
            state["current_step"] = "create_outline"
        elif current_step == "review_outline":
            state["current_step"] = "develop_section"
        elif current_step == "review_section":
            if story.current_section_index < len(story.sections) - 1:
                story.current_section_index += 1
                state["current_step"] = "develop_section"
            else:
                state["current_step"] = "complete"
        elif current_step == "review_images":
            if story.current_section_index < len(story.sections) - 1:
                story.current_section_index += 1
                state["current_step"] = "develop_section"
            else:
                state["current_step"] = "complete"
    else:
        # Handle rejection/revision based on feedback
        state["current_step"] = f"revise_{state['current_step']}"
    
    return state

def should_continue(state: StoryState) -> str:
    """Determine the next step in the workflow."""
    current_step = state["current_step"]
    
    if current_step == "complete":
        return "end"
    elif current_step.startswith("review_"):
        return "feedback"
    elif current_step == "create_outline":
        return "outline"
    elif current_step == "develop_section":
        return "section"
    elif current_step.startswith("revise_"):
        # Handle revision workflow
        original_step = current_step.replace("revise_", "")
        if original_step == "review_synopsis":
            return "synopsis"
        elif original_step == "review_outline":
            return "outline"
        elif original_step == "review_section":
            return "section"
        elif original_step == "review_images":
            return "images"
    
    return "synopsis"

def create_story_graph(llm: ChatOpenAI) -> Graph:
    """Create the story generation workflow graph."""
    
    workflow = StateGraph(StoryState)
    
    # Add nodes for each step
    workflow.add_node("synopsis", lambda x: create_synopsis(x, llm))
    workflow.add_node("outline", lambda x: create_outline(x, llm))
    workflow.add_node("section", lambda x: develop_section(x, llm))
    workflow.add_node("images", lambda x: generate_images(x, llm))
    workflow.add_node("feedback", process_feedback)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "synopsis",
        should_continue,
        {
            "feedback": "feedback",
            "outline": "outline",
            "end": "end"
        }
    )
    
    workflow.add_conditional_edges(
        "outline",
        should_continue,
        {
            "feedback": "feedback",
            "section": "section",
            "end": "end"
        }
    )
    
    workflow.add_conditional_edges(
        "section",
        should_continue,
        {
            "feedback": "feedback",
            "images": "images",
            "end": "end"
        }
    )
    
    workflow.add_conditional_edges(
        "images",
        should_continue,
        {
            "feedback": "feedback",
            "section": "section",
            "end": "end"
        }
    )
    
    workflow.add_conditional_edges(
        "feedback",
        should_continue,
        {
            "synopsis": "synopsis",
            "outline": "outline",
            "section": "section",
            "images": "images",
            "end": "end"
        }
    )
    
    # Add end node
    workflow.add_node("end", lambda x: x)
    
    # Set entry point
    workflow.set_entry_point("synopsis")
    
    return workflow.compile()

def create_initial_state(parameters: StoryParameters) -> StoryState:
    """Create the initial state for the story graph."""
    return {
        "story": Story(
            title="",
            parameters=parameters,
            synopsis="",
            sections=[],
            current_section_index=0
        ),
        "current_step": "synopsis",
        "user_feedback": "",
        "approved": False
    } 