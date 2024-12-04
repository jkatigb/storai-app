import asyncio
from models import (
    Story, StoryParameters, Character, StorySection, Scene,
    synopsis_agent, outline_agent, outline_expansion_agent,
    scene_setting_agent, scene_dialogue_agent,
    process_scenes_parallel,
    StoryDeps, OutlineExpansionDeps
)

async def main():
    try:
        # Create story parameters
        story_params = StoryParameters(
            age_range="4-6",
            themes=["friendship", "courage", "problem-solving"],
            moral="Working together makes us stronger",
            characters=[
                Character(
                    name="Luna",
                    description="A curious young rabbit who loves to explore",
                    role="protagonist",
                    traits=["curious", "brave", "friendly"]
                ),
                Character(
                    name="Oliver",
                    description="A wise old owl who helps guide Luna",
                    role="mentor",
                    traits=["wise", "patient", "kind"]
                ),
                Character(
                    name="Sparkle",
                    description="A magical firefly with a bright spirit",
                    role="friend",
                    traits=["cheerful", "helpful", "energetic"]
                ),
                Character(
                    name="Maple",
                    description="A gentle deer who loves to dance",
                    role="friend",
                    traits=["graceful", "kind", "playful"]
                ),
                Character(
                    name="Nutkin",
                    description="A mischievous squirrel with quick wit",
                    role="friend",
                    traits=["clever", "energetic", "funny"]
                )
            ],
            story_setting="An enchanted forest with magical creatures",
            tone="Whimsical and encouraging",
            book_type="picture book",
            story_length="1500 words",  # Increased for more detailed scenes
            target_scenes=15  # More scenes for better pacing
        )

        # Create initial story structure
        story = Story(
            title="Luna's Forest Adventure",
            parameters=story_params
        )

        print("\n=== Story Generation Process ===\n")
        
        print("1. Generating Synopsis...")
        synopsis_result = await synopsis_agent.run(
            "Create a synopsis for this children's story",
            deps=StoryDeps(story=story.model_dump())
        )
        if synopsis_result and synopsis_result.data:
            story.synopsis = synopsis_result.data
            print(f"\nSynopsis:\n{story.synopsis}\n")

        print("\n2. Generating Initial Outline...")
        outline_result = await outline_agent.run(
            "Create a detailed outline for this story",
            deps=StoryDeps(story=story.model_dump())
        )
        if outline_result and outline_result.data:
            story.sections = outline_result.data
            print("\nInitial Outline:")
            for section in story.sections:
                print(f"\n{section.name}:")
                print(f"Outline: {section.outline}")
                print(f"Moral Integration: {section.moral_integration}")

        print("\n3. Expanding Outline (Depth 1)...")
        expansion_result = await outline_expansion_agent.run(
            "Expand this outline with broad story arcs",
            deps=OutlineExpansionDeps(
                story=story.model_dump(),
                sections=[section.model_dump() for section in story.sections],
                depth=1
            )
        )
        if expansion_result and expansion_result.data:
            story.sections = expansion_result.data
            print("\nFirst Expansion:")
            for section in story.sections:
                print(f"\n{section.name}:")
                print(f"Outline: {section.outline}")
                print(f"Moral Integration: {section.moral_integration}")

        print("\n4. Expanding Outline (Depth 2)...")
        expansion_result = await outline_expansion_agent.run(
            "Expand this outline with character moments",
            deps=OutlineExpansionDeps(
                story=story.model_dump(),
                sections=[section.model_dump() for section in story.sections],
                depth=2
            )
        )
        if expansion_result and expansion_result.data:
            story.sections = expansion_result.data
            print("\nSecond Expansion:")
            for section in story.sections:
                print(f"\n{section.name}:")
                print(f"Outline: {section.outline}")
                print(f"Moral Integration: {section.moral_integration}")

        print("\n5. Generating Scenes...")
        processed_sections = await process_scenes_parallel(
            [section.model_dump() for section in story.sections],
            story.parameters.model_dump()
        )
        if processed_sections:
            story.sections = processed_sections
            print("\nComplete Story Text:")
            for section in story.sections:
                print(f"\n=== {section.name} ===\n")
                for i, scene in enumerate(section.scenes, 1):
                    print(f"\nScene {i}:")
                    print(f"Setting: {scene.setting}")
                    print(f"Mood: {scene.mood}")
                    print("\nCharacters Present:")
                    for char in scene.characters:
                        print(f"- {char.name} ({char.role})")
                    print("\nAction:")
                    print(scene.action)
                    print("\nScene:")
                    if scene.dialogue_segments:
                        for dialogue in scene.dialogue_segments:
                            print(f"\n{dialogue['speaker']} {dialogue['action']}")
                            print(f'"{dialogue["text"]}"')
                    else:
                        print(scene.text)
                    print("-" * 80)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

    return story

if __name__ == "__main__":
    asyncio.run(main()) 