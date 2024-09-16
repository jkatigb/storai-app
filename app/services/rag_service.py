import os
import pinecone
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple
from ..models import StoryParameters, StoryOutline

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv("PINECONE_API_KEY"),
            environment=os.getenv("PINECONE_ENVIRONMENT")
        )
        
        # Create or connect to the indexes
        self.story_index = pinecone.Index("story-outlines")
        self.section_index = pinecone.Index("story-sections")

    def _encode_parameters(self, params: StoryParameters) -> List[float]:
        text = f"{params.age_range} {' '.join(params.themes)} {params.moral} {params.story_setting} {params.tone}"
        return self.model.encode([text])[0].tolist()

    def _encode_section(self, section_name: str, section_content: List[str]) -> List[float]:
        text = f"{section_name}: {' '.join(section_content)}"
        return self.model.encode([text])[0].tolist()

    def add_story(self, params: StoryParameters, outline: StoryOutline):
        story_embedding = self._encode_parameters(params)
        self.story_index.upsert(vectors=[(str(outline.title), story_embedding, {
            "params": params.dict(),
            "outline": outline.dict()
        })])

        # Add each section to the section index
        for section_name, section_content in outline.plot.items():
            section_embedding = self._encode_section(section_name, section_content)
            self.section_index.upsert(vectors=[(f"{outline.title}_{section_name}", section_embedding, {
                "story_title": outline.title,
                "section_name": section_name,
                "section_content": section_content
            })])

    def find_similar_story(self, params: StoryParameters, threshold: float = 0.8) -> Tuple[StoryOutline, float]:
        query_embedding = self._encode_parameters(params)
        results = self.story_index.query(query_embedding, top_k=1, include_metadata=True)
        
        if results.matches and results.matches[0].score < threshold:
            match = results.matches[0]
            return StoryOutline(**match.metadata["outline"]), match.score
        return None, None

    def find_similar_section(self, section_name: str, section_content: List[str], threshold: float = 0.8) -> Tuple[Dict, float]:
        query_embedding = self._encode_section(section_name, section_content)
        results = self.section_index.query(query_embedding, top_k=1, include_metadata=True)

        if results.matches and results.matches[0].score < threshold:
            match = results.matches[0]
            return match.metadata, match.score
        return None, None

rag_service = RAGService()