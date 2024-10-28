import sys, os
if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from tqdm import tqdm
from pathlib import Path
from typing import List, Dict, Any, TypedDict
from dataclasses import dataclass

from prompts import StoryboarderPrompts, Styles
from generators.LLM import LLM

@dataclass
class Scene:
    text: str 
    image: str

@dataclass 
class Storyboard:
    scenes: List[Scene]

    @classmethod
    def load(cls, filename: Path) -> 'Storyboard':
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            scenes = [Scene(text=scene['text'], image=scene['image']) for scene in data]
            return cls(scenes=scenes)
    
    def save(self, filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        data = [{"text": scene.text, "image": scene.image} for scene in self.scenes]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def update(cls, filename: Path, updates: 'Storyboard') -> None:
        storyboard = cls.load(filename)
        for i, update_scene in enumerate(updates.scenes):
            if i < len(storyboard.scenes):
                storyboard.scenes[i].text = update_scene.text  
                storyboard.scenes[i].image = update_scene.image
        storyboard.save(filename)

class Storyboarder():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_storyboard(self, text: str) -> Storyboard:
        visual_description = self.llm.generate_text(
            prompt = StoryboarderPrompts.User.generate_storyboard_visual_analysis(text=text),
        ).extract_tag('visual_description')

        storyboard = self.llm.generate_text(
            prompt = StoryboarderPrompts.User.generate_storyboard_scenes(text=text, context=visual_description),
        ).extract_tag('result')

        storyboard_parsed = json.loads(storyboard)
        scenes = [Scene(text=scene['text'], image=scene['image']) for scene in storyboard_parsed]
        return Storyboard(scenes=scenes)
    
    def generate_tumbnail(self, text: str) -> str:
        output = self.llm.generate_text(
            prompt = StoryboarderPrompts.User.generate_tumbnail(text),
        )['text']
        return output

    def _chunk_text(self, text: str, chunk_size: int):
        lines = text.splitlines()
        for i in range(0, len(lines), chunk_size):
            yield '\n'.join(lines[i:i+chunk_size])

if __name__ == "__main__":
    from generators.LLM import Models

    text = Path('data/MITO_TV/SHORTS/S_MITOS_GRIEGOS/1/text/text.txt').read_text(encoding='utf-8')
    
    storyboarder = Storyboarder(LLM(model=Models.Anthropic.CLAUDE_3_5_sonnet))
    storyboard = storyboarder.generate_storyboard(text=text)
    storyboard.save(Path('storyboard.json'))
    storyboard2 = Storyboard.load(Path('storyboard.json'))

    updated_scenes = [
        Scene(text="Modified text for scene 1", image="Modified image prompt 1"),
        Scene(text="Modified text for scene 2", image="Modified image prompt 2")
    ]
    updates = Storyboard(scenes=updated_scenes)
    
    # Update the storyboard file with the changes
    Storyboard.update(Path('storyboard.json'), updates)
    
    # Load the updated storyboard to verify changes
    updated_storyboard = Storyboard.load(Path('storyboard.json'))
    updated_storyboard