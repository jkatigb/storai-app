from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from .models import StorySegment, Story

# Prompt templates
story_start_template = """
You are a creative storyteller. Create an engaging story based on the following parameters:
Genre: {genre}
Theme: {theme}
Length: {length}

Generate a story title and the first segment of the story. The story should be engaging and leave room for the reader to make choices about what happens next.
Provide 2-3 possible choices for what could happen next.

{format_instructions}
"""

story_continue_template = """
Previous story segments:
{previous_segments}

Current situation:
{current_segment}

User's choice: {user_choice}

Continue the story based on the user's choice. Make it engaging and provide 2-3 new choices for what could happen next.

{format_instructions}
"""

class StoryChain:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=Story)
        self.segment_parser = PydanticOutputParser(pydantic_object=StorySegment)
        
        # Initialize chains
        self.start_chain = self._create_start_chain()
        self.continue_chain = self._create_continue_chain()
    
    def _create_start_chain(self):
        prompt = ChatPromptTemplate.from_template(
            template=story_start_template,
        )
        return LLMChain(llm=self.llm, prompt=prompt)
    
    def _create_continue_chain(self):
        prompt = ChatPromptTemplate.from_template(
            template=story_continue_template,
        )
        return LLMChain(llm=self.llm, prompt=prompt)
    
    async def start_story(self, genre: str, theme: str, length: str = "medium") -> Story:
        response = await self.start_chain.arun(
            genre=genre,
            theme=theme,
            length=length,
            format_instructions=self.parser.get_format_instructions()
        )
        return self.parser.parse(response)
    
    async def continue_story(self, story: Story, user_choice: str) -> StorySegment:
        previous_segments = "\n".join(
            [f"Segment {i}: {seg.content}" for i, seg in enumerate(story.previous_segments, 1)]
        )
        
        response = await self.continue_chain.arun(
            previous_segments=previous_segments,
            current_segment=story.current_segment.content,
            user_choice=user_choice,
            format_instructions=self.segment_parser.get_format_instructions()
        )
        return self.segment_parser.parse(response) 