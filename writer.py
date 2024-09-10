import json
import textwrap
from typing import List
from pathlib import Path

from tqdm import tqdm

import prompts
from LLM import LLM
from definitions import Scene

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_video_script(self, content: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
                system_prompt= prompts.Prompts.ESP.GUION_SHORT_VIRAL,
                system_examples= '', 
                human_prompt= "Escribe el script para un video sobre {content}".format(content=content),
                output_format = 
                    prompts.OutputFormats.ESP.NUMERO_PALABRAS.format(words_number=words_number) + 
                    prompts.OutputFormats.ESP.SIN_SALTOS_DE_LINEA
        )
        return text
    
    def generate_storyboard(self, text: str, style: str = None) -> List[Scene]:
        output = self.llm.generate_text(
            system_prompt=prompts.OutputFormats.ENG.GENERATE_STORYBOARD + style,
            system_examples='',
            human_prompt="Create a storyboard for this text: {text}".format(text=text),
            output_format=prompts.OutputFormats.ENG.GENERATE_STORYBOARD_OUTPUT_FORMAT
        )
        storyboard_parsed = json.loads(output)
        storyboard = [Scene(text=scene['text'], image=scene['image']) for scene in storyboard_parsed]
        return storyboard
    
    def save_script(self, script: str, filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(script, encoding='utf-8')

    def save_storyboard(self, storyboard: List[Scene], filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)

class BookWriter(Writer):
    def __init__(self, llm: LLM) -> None:
        super().__init__(llm)

    def generate_storyboard_from_long_text(self, text: str, style: str = None, batch_size: int = 10) -> List[Scene]:
        storyboard = []
        
        for chunk in tqdm(list(self._chunk_text(text, batch_size)), desc="Generating storyboard"):
            chunk_storyboard = self.generate_storyboard(text=chunk, style=style)
            storyboard.extend(chunk_storyboard)

        return storyboard
    
    def generate_short_script_from_content(self, chapter_content: str, theme: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
            system_prompt=textwrap.dedent(f'''
                Aqui tienes el capitulo de la iliada:
                {chapter_content}
                {prompts.Prompts.ESP.REGLAS_STORYTELLING}
                {prompts.Prompts.ESP.PRESENTACION_PERSONAJES}
            ''').strip(),
            human_prompt=f'Escribe un video viral inspirado en este capitulo, enfocándote en el tema: {theme}',
            output_format = 
                prompts.OutputFormats.ESP.NUMERO_PALABRAS.format(words_number=words_number) + 
                prompts.OutputFormats.ESP.SIN_SALTOS_DE_LINEA
        )
        return text
    
    def improve_text_storytelling(self, text: str, words_number: int = 100) -> str:
        text_improved = self.llm.generate_text(
            system_prompt=textwrap.dedent(f'''
                Mejora este texto siguiendo las reglas de storytelling:
                {text}
                {prompts.Prompts.ESP.REGLAS_STORYTELLING}
                {prompts.Prompts.ESP.PRESENTACION_PERSONAJES}
            ''').strip(),
            human_prompt='Escribe solo el texto mejorado, no des explicaciones',
            output_format = 
                prompts.OutputFormats.ESP.NUMERO_PALABRAS.format(words_number=words_number) + 
                prompts.OutputFormats.ESP.SIN_SALTOS_DE_LINEA
        )
        return text_improved

    def _chunk_text(self, text: str, chunk_size: int):
        lines = text.splitlines()
        for i in range(0, len(lines), chunk_size):
            yield '\n'.join(lines[i:i+chunk_size])

if __name__ == "__main__":
    from LLM import GPT4o, Claude35Sonnet
    
    writer = BookWriter(
        llm=Claude35Sonnet(
            low_vram=False,
            llm_config={'temperature': 0.5}
        )
    )

    N = 3
    LONG_TEXT = Path('data\TERROR\LaGallinaDegollada.txt').read_text(encoding='utf-8')
    storyboard = writer.generate_storyboard_from_long_text(
        text=LONG_TEXT, 
        style=prompts.Styles.Flux.DARK_ATMOSPHERE
    )
    writer.save_storyboard(storyboard, (Path('data\TERROR') / f'{N}/text/storyboard.json'))