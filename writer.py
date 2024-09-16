import json
import textwrap
from typing import List
from pathlib import Path

from tqdm import tqdm

from prompts import Prompts, OutputFormats, WriterPrompts
from LLM import LLM
from definitions import Scene

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_story(self, content: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
            system_prompt=WriterPrompts.REGLAS_STORYTELLING,
            human_prompt= f"Utiliza el storytelling para escribir {content}",
            output_format = 
                OutputFormats.ESP.NUMERO_PALABRAS.format(words_number=words_number) +
                WriterPrompts.SALTO_DE_LINEA_SIMPLE
        )
        return text
    
    def save_text(self, text: str, save_path: Path) -> None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(text, encoding='utf-8')

if __name__ == "__main__":
    from LLM import GPT4o, Claude35Sonnet
    
    N = 3
    writer = Writer(
        llm=Claude35Sonnet(
            low_vram=False,
            llm_config={
                'temperature': 0.5,
            }
        )
    )
    text = writer.generate_story(
        content='El mito nordico sobre El Árbol del Mundo Yggdrasil y los Nueve Mundos: Conexión de todos los reinos de la existencia.',
        words_number=120
    )
    print(text)
    print(f"Characters: {len(text)}")
    writer.save_text(
        text=text,
        save_path=Path(f'data/MITO_TV/SHORTS/MITOS_NORDICOS/{N}/text/text.txt')
    )