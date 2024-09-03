import json
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
                system_prompt= prompts.Prompts.ESP.GUION_VIDEO_VIRAL,
                system_examples= '', 
                human_prompt= "Escribe el script para un video sobre {content}".format(content=content),
                output_format = 
                    prompts.OutputFormats.ESP.NUMERO_PALABRAS.format(words_number=words_number) + 
                    prompts.OutputFormats.ESP.SIN_SALTOS_DE_LINEA
        )
        return text
    
    def split_text(self, text: str) -> List[str]:
        output = self.llm.generate_text(
            system_prompt=prompts.OutputFormats.ENG.SPLIT_TEXT_SCENES,
            system_examples='',
            human_prompt="Transform this text: {text}. Return only an array [] do not write any additional text.".format(text=text),
            output_format=''
        )
        text_splited_parsed = json.loads(output)
        return text_splited_parsed
    
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
    
    def save_storyboard(self, storyboard: List[Scene], filename: Path):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)


class BookWriter(Writer):
    def __init__(self, llm: LLM) -> None:
        super().__init__(llm)

    def generate_storyboard_from_chapter(self, filename: Path, batch_size: int = 10) -> List[Scene]:
        storyboard = []
        
        for chunk in tqdm(list(self._chunk_file(filename, batch_size)), desc="Generating storyboard"):
            chunk_storyboard = self.generate_storyboard(chunk)
            storyboard.extend(chunk_storyboard)

        return storyboard

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
            llm_config={'temperature': 0.8}
        )
    )
    storyboard = writer.generate_storyboard_from_chapter(Path('data\HOMERO\LA_ILIADA\CAPITULO_001\CAPITULO_001.txt'))
    writer.save_storyboard(storyboard, Path('data\HOMERO\LA_ILIADA\CAPITULO_001\CAPITULO_001_STORYBOARD.json'))
