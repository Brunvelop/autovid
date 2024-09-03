import os
from typing import Union
from pathlib import Path
from dotenv import load_dotenv
from abc import ABC, abstractmethod

import torch
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig

from definitions import LLMModels

class LLM(ABC):
    def __init__(
        self, 
        cache_dir: Path = Path('./models'), 
        low_vram: bool = False, 
        llm_config: dict = {}
    ):
        load_dotenv()
        self.cache_dir = cache_dir
        self.chat_model = self._load_chat_model(low_vram, llm_config)

    @abstractmethod
    def generate_text(
            self, 
            system_memory: str = '',
            system_prompt: str = '',
            system_examples: str = '', 
            human_prompt: str = '',
            output_format: str = ''
        ) -> str:
        pass

    @abstractmethod
    def _load_chat_model(self, low_vram: bool, llm_config: dict) -> Union[ChatOpenAI, HuggingFacePipeline]:
        pass

class OpenAILLM(LLM, ABC):
    def generate_text(
            self, 
            system_memory: str = '',
            system_prompt: str = '',
            system_examples: str = '', 
            human_prompt: str = '',
            output_format: str = ''
        ) -> str:
        system_str = '\n'.join(filter(bool, [system_memory, system_prompt, system_examples]))
        human_str = '\n'.join(filter(bool, [human_prompt, output_format]))
        messages = [SystemMessage(system_str), HumanMessage(human_str)]
        output = self.chat_model(messages)
        return output.content

    def _load_chat_model(self, low_vram: bool, llm_config: dict) -> ChatOpenAI:
        return ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name=self.model_name,
            temperature=llm_config.get('temperature', 0.8),
        )

class GPT4o(OpenAILLM):
    model_name = LLMModels.GPT4o.value

class GPT4oMini(OpenAILLM):
    model_name = LLMModels.GPT4oMini.value

class LLAMA31_8B(LLM):
    pass

if __name__ == "__main__":
    llm = GPT4o(
        low_vram=False,
        llm_config={'temperature': 0}
    )
    memory = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x']
    for _ in range(5):
        text = llm.generate_text(
                system_memory= 'memoria = '+ str(memory),
                system_prompt= 'Eres un sistema que genera letras aleatorias en minuscula que no esten en memoria',
                system_examples= 'Debes devolver algo asi: z o w o b o x pero que no este en memoria', 
                human_prompt= 'dame una letra',
                output_format = 'devuelve solo una letra en minuscula, fijate en memoria = [] para ver las que no puedes devolver, no repitas ninguna de memoria. Si no quedan letras dispobiles devuelve solo "None", no añadas mas texto'
        )
        print("Letra:", text)
        if text == 'None':
            print(text)
        memory.append(text)