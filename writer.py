import json
from typing import List

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


if __name__ == "__main__":
    from definitions import LLMModels
    llm = LLM(
        model_id=LLMModels.GPT4o,
        low_vram=False,
        llm_config={'temperature': 0.8}
    )
    writer = Writer(llm=llm)
    text = writer.generate_video_script(content='Una historia de amor', words_number=100)
    print(text)
    splited_text = writer.generate_storyboard(text)
    print(splited_text)
