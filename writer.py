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
    
    def generate_storyboard(self, text: str) -> List[Scene]:
        output = self.llm.generate_text(
            system_prompt=prompts.OutputFormats.ENG.GENERATE_STORYBOARD,
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

    def generate_storyboard_from_chapter(self, full_chapter_path: Path, batch_size: int = 10) -> List[Scene]:
        storyboard = []
        
        for chunk in tqdm(list(self._chunk_file(full_chapter_path, batch_size)), desc="Generating storyboard"):
            chunk_storyboard = self.generate_storyboard(chunk)
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

    def _chunk_file(self, file_path: Path, chunk_size: int):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(0, len(lines), chunk_size):
                yield ''.join(lines[i:i+chunk_size])

if __name__ == "__main__":
    from LLM import GPT4o
    
    writer = BookWriter(
        llm=GPT4o(
            low_vram=False,
            llm_config={'temperature': 0.5}
        )
    )

    SHORT_N = 2
    THEME = "La ira de Aquiles como tema central del poema."

    CAPITULO1_FOLDER = Path('data/HOMERO/LA_ILIADA/CAPITULO_001')
    SHORTS_FOLDER = (CAPITULO1_FOLDER / 'SHORTS')
    CAPITULO1 = (CAPITULO1_FOLDER / 'CAPITULO_001.txt').read_text(encoding='utf-8')
    
    text = writer.generate_short_script_from_content(
        chapter_content=CAPITULO1,
        theme=THEME,
        words_number=100
    )
    text_improved = writer.improve_text_storytelling(text, words_number=100)

    print(f'{text} \n ->{text_improved} \n')

    storyboard = writer.generate_storyboard(text_improved)
    writer.save_storyboard(text_improved, (SHORTS_FOLDER / f'{SHORT_N}/text/script.txt'))
    writer.save_storyboard(storyboard, (SHORTS_FOLDER / f'{SHORT_N}/text/storyboard.json'))