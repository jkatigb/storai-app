from pydantic import BaseModel
from typing import List, Dict
from uuid import UUID, uuid4

class Character(BaseModel):
    name: str
    description: str

class StoryParameters(BaseModel):
    age_range: str
    themes: List[str]
    moral: str
    characters: List[Character]
    story_setting: str
    tone: str
    parental_concerns: List[str] = []
    inclusion_and_diversity: str = ""
    ending: str = ""

class Scene(BaseModel):
    setting: str
    characters: List[Dict]
    text: str
    image_prompt: str
    image_url: str = ""

class SectionState(BaseModel):
    name: str
    outline: str
    scenes: List[Scene]

class StoryOutline(BaseModel):
    previous_story: str = ""
    title: str
    setting: List[str]
    characters: List[str]
    themes: List[str]
    moral: str
    style: str
    plot: Dict[str, List[str]]

class User(BaseModel):
    id: UUID = uuid4()
    username: str

class StoryRequest(BaseModel):
    user_id: UUID
    parameters: StoryParameters

class QueuedTask(BaseModel):
    id: UUID = uuid4()
    user_id: UUID
    task_type: str
    parameters: dict
    status: str = "queued"