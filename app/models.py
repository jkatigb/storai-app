import os
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
import openai
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Story Models
class Character(BaseModel):
    name: str
    description: str
    role: str
    traits: List[str]

class StoryParameters(BaseModel):
    age_range: str
    themes: List[str]
    moral: str
    characters: List[Character]
    story_setting: str
    tone: str
    book_type: str
    story_length: str
    target_scenes: int

class Scene(BaseModel):
    setting: str
    action: str
    text: str
    characters: List[Character]
    mood: str
    dialogue_segments: List[dict] = Field(
        description="List of dialogue segments, each containing speaker, text, and associated action",
        default_factory=list
    )

class SceneSetting(BaseModel):
    setting: str
    mood: str
    characters: List[Character]

class SceneDialogue(BaseModel):
    action: str
    text: str
    dialogue_segments: List[dict] = Field(
        description="List of dialogue segments, each containing speaker, text, and associated action",
        default_factory=list
    )

class StorySection(BaseModel):
    name: str
    outline: str
    moral_integration: str
    scenes: List[Scene] = []

class Story(BaseModel):
    title: str
    parameters: StoryParameters
    synopsis: Optional[str] = None
    sections: List[StorySection] = []

@dataclass
class StoryDeps:
    story: dict

# Initialize agents for different tasks
synopsis_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=StoryDeps,
    result_type=str,
    system_prompt="""You are an expert children's book editor.
    Your task is to create engaging synopses that:
    1. Capture the essence of the story
    2. Appeal to both children and parents
    3. Highlight the moral lesson naturally
    4. Set appropriate expectations
    5. Use age-appropriate language"""
)

@synopsis_agent.tool
def get_story_parameters(ctx: RunContext[StoryDeps]) -> str:
    """Get formatted story parameters for synopsis generation."""
    params = ctx.deps.story["parameters"]
    return f"""Create a brief, engaging synopsis for a {params['book_type']} with:
    Title: {ctx.deps.story['title']}
    Age Range: {params['age_range']}
    Themes: {', '.join(params['themes'])}
    Moral: {params['moral']}
    Characters:
{chr(10).join('    - ' + char['name'] + ' (' + char['role'] + '): ' + char['description'] + ', traits: ' + ', '.join(char['traits']) for char in params['characters'])}
    Setting: {params['story_setting']}
    Tone: {params['tone']}
    Target Length: {params['story_length']}
    
    The synopsis should be 2-3 sentences long and capture the essence of the story."""

outline_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=StoryDeps,
    result_type=List[StorySection],
    system_prompt="""You are an expert children's book author and story structure specialist.
    Your task is to create structured outlines that:
    1. Follow a clear narrative arc
    2. Integrate moral lessons naturally
    3. Maintain consistent pacing
    4. Create engaging story beats
    5. Consider the age of the audience
    6. Ensure each section can be divided into the target number of scenes

    When including characters in scenes, make sure to include all their required fields:
    - name: The character's name
    - description: A brief description of the character
    - role: The character's role (protagonist, mentor, etc.)
    - traits: A list of character traits"""
)

@outline_agent.tool
def get_story_context(ctx: RunContext[StoryDeps]) -> str:
    """Get formatted story context for outline generation."""
    params = ctx.deps.story["parameters"]
    characters = []
    for char in params['characters']:
        characters.append(f"{char['name']} ({char['role']}): {char['description']}, traits: {', '.join(char['traits'])}")
    
    return f"""Create a structured outline for a {params['book_type']} with:
    Title: {ctx.deps.story['title']}
    Synopsis: {ctx.deps.story['synopsis']}
    Age Range: {params['age_range']}
    Themes: {', '.join(params['themes'])}
    Moral: {params['moral']}
    Characters:
{chr(10).join('    - ' + char for char in characters)}
    Setting: {params['story_setting']}
    Tone: {params['tone']}
    Target Scenes: {params['target_scenes']}
    Target Length: {params['story_length']}
    
    Divide the story into Introduction, Conflict, Rising Action, Climax, Falling Action, and Resolution.
    Each section should be structured to accommodate approximately {params['target_scenes'] // 6} scenes
    while maintaining natural story flow and pacing.
    
    For each scene, make sure to include the characters with all their required fields:
    - name: The character's name
    - description: A brief description of the character
    - role: The character's role (protagonist, mentor, etc.)
    - traits: A list of character traits"""

@dataclass
class OutlineExpansionDeps:
    story: dict
    sections: List[dict]
    depth: int = 1

outline_expansion_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=OutlineExpansionDeps,
    result_type=List[StorySection],
    system_prompt="""You are an expert children's book author specializing in detailed story development.
    Your task is to expand the basic outline into a richer, more detailed structure:
    1. Add more specific plot points to each section
    2. Develop character arcs and growth moments
    3. Identify emotional beats and tension points
    4. Plan how the moral lesson develops through each section
    5. Create natural transitions between sections
    6. Ensure consistent character development
    7. Maintain age-appropriate complexity and pacing
    
    For each section, provide:
    - name: The section name (Introduction, Conflict, etc.)
    - outline: Expanded outline with more details
    - moral_integration: How this section develops the moral lesson
    - scenes: Leave this empty, it will be filled in later"""
)

@outline_expansion_agent.tool
def get_outline_context(ctx: RunContext[OutlineExpansionDeps]) -> str:
    """Get formatted context for outline expansion."""
    params = ctx.deps.story["parameters"]
    characters = []
    for char in params['characters']:
        characters.append(f"{char['name']} ({char['role']}): {char['description']}, traits: {', '.join(char['traits'])}")
    
    sections = []
    for section in ctx.deps.sections:
        sections.append(f"{section['name']}:\n{section['outline']}\n{section['moral_integration']}")
    
    return f"""Expand this outline for a {params['book_type']} with:
    Title: {ctx.deps.story.get('title', 'Story')}
    Synopsis: {ctx.deps.story.get('synopsis', '')}
    Age Range: {params['age_range']}
    Themes: {', '.join(params['themes'])}
    Moral: {params['moral']}
    Characters:
{chr(10).join('    - ' + char for char in characters)}
    Setting: {params['story_setting']}
    Tone: {params['tone']}
    Expansion Depth: {ctx.deps.depth}
    
    Current Outline:
{chr(10).join('    ' + section for section in sections)}
    
    For each section, provide:
    1. More specific plot points and story beats
    2. Character development moments
    3. Emotional beats and tension points
    4. How the moral lesson develops
    5. Natural transitions between scenes
    
    Keep the same section structure but add more detail and depth to each part.
    Since this is expansion depth {ctx.deps.depth}, {
        'focus on broad story arcs and major plot points.' if ctx.deps.depth == 1 else
        'add more specific details and character moments.' if ctx.deps.depth == 2 else
        'dive deep into emotional beats and subtle character development.'
    }
    Do not include any scenes yet, they will be added later."""

@dataclass
class SceneSettingDeps:
    story: dict
    section: dict
    previous_sections: List[dict]

scene_setting_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SceneSettingDeps,
    result_type=List[SceneSetting],
    system_prompt="""You are an expert children's book author specializing in scene setting.
    Your task is to create vivid and engaging scene settings that:
    1. Create a rich, immersive environment
    2. Set the right mood and atmosphere
    3. Support the story's themes
    4. Maintain consistency with previous scenes
    5. Keep settings age-appropriate and engaging"""
)

@scene_setting_agent.tool
def get_scene_setting_context(ctx: RunContext[SceneSettingDeps]) -> str:
    """Get formatted context for scene setting generation."""
    params = ctx.deps.story["parameters"]
    characters = []
    for char in params['characters']:
        characters.append(f"{char['name']} ({char['role']}): {char['description']}, traits: {', '.join(char['traits'])}")
    
    previous_sections = []
    for section in ctx.deps.previous_sections:
        scenes = []
        for scene in section.get('scenes', []):
            if isinstance(scene, Scene):
                scene = scene.model_dump()
            scenes.append(f"Setting: {scene['setting']}\nMood: {scene['mood']}")
        previous_sections.append(f"{section['name']}:\n{section['outline']}\nScenes:\n{chr(10).join(scenes)}")
    
    return f"""Create scene settings for this section of a {params['book_type']} with:
    Title: {ctx.deps.story.get('title', 'Story')}
    Age Range: {params['age_range']}
    Setting: {params['story_setting']}
    Tone: {params['tone']}
    Characters:
{chr(10).join('    - ' + char for char in characters)}
    
    Story So Far:
{chr(10).join('    ' + section for section in previous_sections)}
    
    Current Section:
    Name: {ctx.deps.section['name']}
    Outline: {ctx.deps.section['outline']}
    
    For each scene setting, provide:
    - setting: Detailed description of the scene location
    - mood: The emotional atmosphere of the scene
    - characters: List of characters present in the scene"""

@dataclass
class SceneDialogueDeps:
    story: dict
    section: dict
    scene_setting: dict
    previous_sections: List[dict]

scene_dialogue_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SceneDialogueDeps,
    result_type=SceneDialogue,
    system_prompt="""You are an expert children's book author specializing in dialogue and action.
    Your task is to create engaging scene content that:
    1. Advances the story naturally
    2. Shows character personality through dialogue
    3. Creates meaningful character interactions
    4. Maintains consistent character voices
    5. Keeps dialogue age-appropriate and engaging"""
)

@scene_dialogue_agent.tool
def get_scene_dialogue_context(ctx: RunContext[SceneDialogueDeps]) -> str:
    """Get formatted context for scene dialogue generation."""
    params = ctx.deps.story["parameters"]
    characters = []
    for char in params['characters']:
        characters.append(f"{char['name']} ({char['role']}): {char['description']}, traits: {', '.join(char['traits'])}")
    
    previous_sections = []
    for section in ctx.deps.previous_sections:
        scenes = []
        for scene in section.get('scenes', []):
            if isinstance(scene, Scene):
                scene = scene.model_dump()
            scenes.append(f"Action: {scene['action']}\nDialogue:\n" + 
                        "\n".join([f"{d['speaker']}: {d['text']} ({d['action']})" 
                                 for d in scene.get('dialogue_segments', [])]))
        previous_sections.append(f"{section['name']}:\n{section['outline']}\nScenes:\n{chr(10).join(scenes)}")
    
    return f"""Create engaging dialogue and action for this scene in a {params['book_type']} with:
    Title: {ctx.deps.story.get('title', 'Story')}
    Age Range: {params['age_range']}
    Tone: {params['tone']}
    Characters:
{chr(10).join('    - ' + char for char in characters)}
    
    Story So Far:
{chr(10).join('    ' + section for section in previous_sections)}
    
    Current Section:
    Name: {ctx.deps.section['name']}
    Outline: {ctx.deps.section['outline']}
    
    Current Scene Setting:
    Setting: {ctx.deps.scene_setting['setting']}
    Mood: {ctx.deps.scene_setting['mood']}
    Characters: {[c['name'] for c in ctx.deps.scene_setting['characters']]}
    
    Create a scene that:
    1. Shows more than tells through dialogue and action
    2. Reveals character personalities through their words and actions
    3. Advances the story through natural conversation
    4. Uses descriptive action tags to show emotions and reactions
    5. Maintains consistent character voices
    
    For each dialogue segment, provide:
    - speaker: The character speaking
    - text: Their actual words
    - action: What they're doing while speaking
    
    Keep the overall scene text around {int(int(params['story_length'].split()[0]) / params['target_scenes'])} words,
    with a good balance of dialogue and narration.
    
    Format the dialogue to be engaging and natural, showing character emotions and reactions through actions rather than telling them."""

@dataclass
class SectionScenesDeps:
    story: dict
    section: dict
    previous_sections: List[dict]
    target_scenes: int = Field(default=3, description="Number of scenes to generate for this section")

section_scenes_agent = Agent(
    'openai:gpt-4o-mini',
    deps_type=SectionScenesDeps,
    result_type=List[SceneSetting],
    system_prompt="""You are an expert children's book author specializing in scene planning.
    Your task is to break down a story section into multiple engaging scenes that:
    1. Flow naturally from one to the next
    2. Build tension and interest progressively
    3. Show character development through action
    4. Create vivid, memorable moments
    5. Maintain consistent pacing"""
)

@section_scenes_agent.tool
def get_section_scenes_context(ctx: RunContext[SectionScenesDeps]) -> str:
    """Get formatted context for scene planning."""
    params = ctx.deps.story["parameters"]
    section_type = ctx.deps.section["name"].lower()
    
    # Adjust number of scenes based on section type
    scene_counts = {
        "introduction": 3,  # Set up characters and world
        "conflict": 2,      # Present the problem
        "rising action": 4, # Build tension
        "climax": 2,       # Peak moment
        "falling action": 2,# Show aftermath
        "resolution": 2     # Wrap up story
    }
    ctx.deps.target_scenes = scene_counts.get(section_type, 3)
    
    return f"""Plan {ctx.deps.target_scenes} scenes for the {section_type} section of this {params['book_type']}.
    
    Section Details:
    Name: {ctx.deps.section['name']}
    Outline: {ctx.deps.section['outline']}
    
    For each scene, create:
    - setting: Where the scene takes place
    - mood: The emotional atmosphere
    - characters: Who is present
    
    Make sure the scenes:
    1. Flow naturally from one to the next
    2. Show progression and development
    3. Build tension appropriately
    4. Create memorable moments
    5. Maintain consistent pacing
    
    This is the {section_type} section, so focus on {
        'introducing characters and the world' if section_type == 'introduction' else
        'presenting the central conflict' if section_type == 'conflict' else
        'building tension and challenges' if section_type == 'rising action' else
        'the peak moment and its impact' if section_type == 'climax' else
        'showing the aftermath and changes' if section_type == 'falling action' else
        'wrapping up loose ends and showing growth' if section_type == 'resolution' else
        'advancing the story naturally'
    }"""

# Parallel processing functions
async def process_scenes_parallel(sections: List[dict], story_parameters: dict) -> List[StorySection]:
    """Process scenes for all sections in parallel."""
    processed_sections = []
    previous_sections = []
    
    for section in sections:
        # First plan the scenes for this section
        scene_settings_result = await section_scenes_agent.run(
            "Plan scenes for this section",
            deps=SectionScenesDeps(
                story={"parameters": story_parameters},
                section=section,
                previous_sections=previous_sections
            )
        )
        
        # Then generate dialogue and action for each scene
        scenes = []
        if scene_settings_result and scene_settings_result.data:
            for scene_setting in scene_settings_result.data:
                dialogue_result = await scene_dialogue_agent.run(
                    "Create dialogue and action for this scene",
                    deps=SceneDialogueDeps(
                        story={"parameters": story_parameters},
                        section=section,
                        scene_setting=scene_setting.model_dump(),
                        previous_sections=previous_sections
                    )
                )
                
                if dialogue_result and dialogue_result.data:
                    # Combine setting and dialogue into a complete scene
                    scene = Scene(
                        setting=scene_setting.setting,
                        mood=scene_setting.mood,
                        characters=scene_setting.characters,
                        action=dialogue_result.data.action,
                        text=dialogue_result.data.text,
                        dialogue_segments=dialogue_result.data.dialogue_segments
                    )
                    scenes.append(scene)
        
        # Update the section with its scenes
        section["scenes"] = scenes
        processed_sections.append(StorySection(**section))
        previous_sections.append(section)
    
    return processed_sections