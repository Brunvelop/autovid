from abc import ABC
from pathlib import Path
import json
import statistics

from generators.LLM import LLM
from tools.writer import Writer

class Agent(ABC):
    def __init__(self, llm: LLM, memory_path: Path):
        self.llm = llm
        self.memory_path = memory_path
        self.memory: list = self._load_memory()

    def _load_memory(self) -> list:
        if self.memory_path.exists():
            memory = self.memory_path.read_text(encoding='utf-8')
            return self._memory_to_list(memory)
        else:
            return []

    def _save_memory(self) -> None:
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(self._memory_to_string(), encoding='utf-8')
    
    def _memory_to_list(self, memory: str) -> list:
        if memory.startswith("<memory>") and memory.endswith("</memory>"):
            memory = memory.strip("<memory></memory>")
            try:
                return eval(memory)
            except:
                return []
        return []

    def _memory_to_string(self) -> str:
        return f"<memory>{self.memory}</memory>"

    def _clean_text(self, text):
        text = text.replace('"', '').replace("'", '')
        return text

class ShortsWriter(Agent):
    def __init__(self, llm: LLM, memory_path: Path, writer: Writer):
        super().__init__(llm, memory_path)
        self.writer = writer

    def generate_serie_stories(self, expertise: str, serie_theme: str, num_stories: int = 5, base_path: Path = None):
        total_cost = 0
        stories = []

        print(f"\nGenerating {num_stories} stories about {serie_theme}...")

        for i in range(num_stories):
            print(f"\n--- Generating story {i+1}/{num_stories} ---")
            
            # Generate theme
            print("Generating theme...")
            theme_response = self.llm.generate_text(
                system_prompt=f'Eres un experto en elegir temas para textos de {expertise}',
                prompt=f"{self._memory_to_string()} No puedes repetir los temas de memoria, elige un nuevo tema relacionado con: {serie_theme}, escribe solo el tema en pocas palabras"
            )
            theme = self._clean_text(theme_response.text)
            total_cost += theme_response.cost
            self.memory.append(theme)
            print(f"Theme generated: {theme}")

            # Generate initial story
            print("Generating initial story...")
            story_response = self.writer.generate_story(expertise, theme)
            total_cost += story_response['cost']
            print("Initial story generated")

            # Improve story
            print("Improving story...")
            improved_response = self.writer.improve_story(expertise, story_response['text'])
            total_cost += improved_response['cost']
            print("Story improved")

            # Evaluate story
            print("Evaluating story...")
            evaluation = self.writer.evaluate_text(improved_response['text'])
            
            # Calculate average score
            scores = [
                evaluation['historical_accuracy'],
                evaluation['storytelling_quality'],
                evaluation['emotional_impact']
            ]
            avg_score = statistics.mean(scores)
            print(f"Story evaluated - Average score: {avg_score:.2f}")

            stories.append({
                'theme': theme,
                'text': improved_response['text'],
                'evaluation': evaluation,
                'avg_score': avg_score
            })

        # Sort stories by average score
        print("\nSorting stories by score...")
        stories.sort(key=lambda x: x['avg_score'], reverse=True)

        # Save stories in order
        print("\nSaving stories...")
        for i, story in enumerate(stories, 1):
            story_path = base_path / str(i)
            text_path = story_path / 'text'
            text_path.mkdir(parents=True, exist_ok=True)

            # Save story text
            (text_path / 'text.txt').write_text(story['text'], encoding='utf-8')
            
            # Save title
            (text_path / 'title.txt').write_text(story['theme'], encoding='utf-8')
            
            # Save evaluation status
            (story_path / 'status.json').write_text(
                json.dumps({
                    'evaluation': story['evaluation'],
                    'average_score': story['avg_score']
                }, indent=2),
                encoding='utf-8'
            )
            print(f"Saved story {i} - Theme: {story['theme']}")

        self._save_memory()
        print(f"\nAll stories generated and saved. Total cost: ${total_cost:.2f}")
        return total_cost

if __name__ == '__main__':
    from generators.LLM import Models
    from pathlib import Path

    memory_path = Path('memory.txt')
    agent = ShortsWriter(
        llm=LLM(model=Models.OpenAI.GPT4o, llm_config={'temperature': 0.5}),
        memory_path=memory_path,
        writer=Writer(LLM(model=Models.OpenAI.GPT4o))
    )

    base_path = Path('data/MITO_TV/SHORTS/S_MITOS_GRIEGOS')
    total_cost = agent.generate_serie_stories(
        expertise='Mitología griega',
        serie_theme='Historias increibles de humanos o humanas relacionadas con la mitología griega',
        num_stories=5,
        base_path=base_path
    )
    print(f'Total cost: ${total_cost}')
