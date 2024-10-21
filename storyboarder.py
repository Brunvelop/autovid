import json
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict, Any, TypedDict

from prompts import StoryboarderPrompts, Styles, OutputFormats
from generators.LLM import LLM

class Scene(TypedDict):
    text: str
    image: str

class Storyboarder():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_storyboard_from_long_text(self, text: str, style: Styles = None, batch_size: int = 10) -> List[Scene]:
        storyboard = []
        
        for chunk in tqdm(list(self._chunk_text(text, batch_size)), desc="Generating storyboard"):
            chunk_storyboard = self.generate_storyboard(text=chunk, style=style)
            storyboard.extend(chunk_storyboard)

        return storyboard
    
    def generate_storyboard(self, text: str, style: Styles = Styles.Flux.MITO_TV) -> List[Scene]:
        output = self.llm.generate_text(
            system_prompt=StoryboarderPrompts.System.GENERATE_STORYBOARD + style,
            prompt = "\n".join([
                f"Create a storyboard for this text: {text}",
                OutputFormats.GENERATE_STORYBOARD_OUTPUT_FORMAT,
            ])
        )['text']
        
        storyboard_parsed = json.loads(output)
        storyboard = [Scene(text=scene['text'], image=scene['image']) for scene in storyboard_parsed]
        return storyboard
    
    def generate_tumbnail(self, text: str) -> str:
        output = self.llm.generate_text(
            system_prompt=StoryboarderPrompts.System.GENERATE_TUMBNAIL,
            prompt = "\n".join([
                f"Generate the description for text: '{text}'",
                OutputFormats.GENERATE_STORYBOARD_OUTPUT_FORMAT,
            ])
        )['text']
        return output
    
    @classmethod
    def load_storyboard(cls, filename: Path) -> List[Dict[str, Any]]:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def save_storyboard(cls, storyboard: List[Dict[str, Any]], filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)

    @classmethod
    def update_storyboard(cls, filename: Path, updates: List[Dict[str, Any]]) -> None:
        storyboard = cls.load_storyboard(filename)
        for update in updates:
            index = update.get('index')
            if index is not None and 0 <= index < len(storyboard):
                for key, value in update.items():
                    if key != 'index':
                        storyboard[index][key] = value
        cls.save_storyboard(storyboard, filename)

    def _chunk_text(self, text: str, chunk_size: int):
        lines = text.splitlines()
        for i in range(0, len(lines), chunk_size):
            yield '\n'.join(lines[i:i+chunk_size])

if __name__ == "__main__":
    from generators.LLM import Models
    
    storyboarder = Storyboarder(LLM(model=Models.Anthropic.CLAUDE_3_5_sonnet))
    
    # Generate the storyboard
    storyboard = storyboarder.generate_storyboard_from_long_text(
        text='Tres niños corrian en la oscuridad, de repente un monstruo verde aparecio. Corrieron sin mirar atrás.', 
        style=Styles.Flux.MITO_TV
    )
    
    # Generate thumbnail
    thumbnail = storyboarder.generate_tumbnail('Los tres niños')

    print(storyboard)
    print('------------')
    print(thumbnail)
