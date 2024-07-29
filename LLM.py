import os
from typing import Union
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, logging
logging.set_verbosity_info()

from definitions import LLMModels

class LLM():
    def __init__(
        self, 
        model_id: LLMModels = LLMModels.GPT4o,
        cache_dir: Path = Path('./models'), 
        low_vram: bool = False, 
        llm_config: dict = {}
    ):
        load_dotenv()
        self.model_id = model_id.value
        self.cache_dir = cache_dir
        self.chat_model = self._load_chat_model(model_id, low_vram, llm_config)

    def _load_chat_model(
            self,
            model_id: LLMModels,
            low_vram: bool,
            llm_config: dict,
        ) -> Union[ChatOpenAI, HuggingFacePipeline]:
        if model_id == LLMModels.GPT4o or model_id == LLMModels.GPT4oMini:
            return ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model_name=model_id.value,
                temperature=llm_config.get('temperature', 0.8),
            )
        elif model_id == LLMModels.INTERNLM7b4b or model_id ==LLMModels.INTERNLM:
            print("Tring to load LLM:", model_id.value)
            tokenizer = AutoTokenizer.from_pretrained(model_id.value, trust_remote_code=True, cache_dir=self.cache_dir)
            model = AutoModelForCausalLM.from_pretrained(
                model_id.value,
                device_map="auto",
                # device=0,  # -1 for CPU
                trust_remote_code=True,
                load_in_4bit=True,
                cache_dir=self.cache_dir,
            )
            pipe = pipeline(model_id.value, model=model, tokenizer=tokenizer)
            print("Loaded!:", model_id.value)
            return HuggingFacePipeline(pipeline=pipe)
        elif model_id == LLMModels.GEMMA2B:
            print("Trying to load LLM:", model_id.value)
            tokenizer = AutoTokenizer.from_pretrained(model_id.value, cache_dir=self.cache_dir)
            model = AutoModelForCausalLM.from_pretrained(
                model_id.value,
                device_map="auto",
                trust_remote_code=True,
                revision="float16",
                cache_dir=self.cache_dir,
            )
            pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
            print("Loaded!:", model_id.value)
            return HuggingFacePipeline(pipeline=pipe)
    
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
        messages = [
            SystemMessage(system_str),
            HumanMessage(human_str)
        ]
        output = self.chat_model(messages)
        return output.content
    

if __name__ == "__main__":
    llm = LLM(
        model_id=LLMModels.GPT4oMini,
        low_vram=False,
        llm_config={'temperature': 0.8}
    )
    memory = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x']
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