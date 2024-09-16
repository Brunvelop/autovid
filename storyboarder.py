import json
import textwrap
from typing import List
from pathlib import Path

from tqdm import tqdm

from prompts import Prompts, OutputFormats, WriterPrompts, Styles
from LLM import LLM
from definitions import Scene

class Storyboarder():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_storyboard_from_long_text(self, text: str, style: Styles = None, batch_size: int = 10) -> List[Scene]:
        storyboard = []
        
        for chunk in tqdm(list(self._chunk_text(text, batch_size)), desc="Generating storyboard"):
            chunk_storyboard = self.generate_storyboard(text=chunk, style=style)
            storyboard.extend(chunk_storyboard)

        return storyboard
    
    def generate_storyboard(self, text: str, style: Styles = Styles.Flux.DARK_ATMOSPHERE) -> List[Scene]:
        output = self.llm.generate_text(
            system_prompt=OutputFormats.ENG.GENERATE_STORYBOARD + style,
            human_prompt="Create a storyboard for this text: {text}".format(text=text),
            output_format=OutputFormats.ENG.GENERATE_STORYBOARD_OUTPUT_FORMAT
        )
        
        storyboard_parsed = json.loads(output)
        storyboard = [Scene(text=scene['text'], image=scene['image']) for scene in storyboard_parsed]
        return storyboard
    
    def save_storyboard(self, storyboard: List[Scene], filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
    
    def _chunk_text(self, text: str, chunk_size: int):
        lines = text.splitlines()
        for i in range(0, len(lines), chunk_size):
            yield '\n'.join(lines[i:i+chunk_size])

if __name__ == "__main__":
    from LLM import GPT4o, Claude35Sonnet
    
    writer = Storyboarder(
        llm=Claude35Sonnet(
            low_vram=False,
            llm_config={'temperature': 0.5}
        )
    )

    N = 1
    TEXT = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/text/text.txt').read_text(encoding='utf-8')
    storyboard = writer.generate_storyboard(
        text=TEXT, 
        style=Styles.Flux.MITO_TV
    )
    writer.save_storyboard(storyboard, (Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/text/storyboard.json')))
    for scene in storyboard:
        print(f"Scene Text: {scene.get('text')}")
        print(f"Image Description: {scene.get('image')}")
        print("-" * 40)