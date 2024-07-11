
import os
import ast
import json
from typing import List, Dict, Union

import torch
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, logging
logging.set_verbosity_info()

import prompts
from definitions import LLMModels, Scene, Storyboard

class ListOfDictsOutputParser:
    def parse(self, output):
        return json.loads(output)

class LLM():
    def __init__(self, model_id: LLMModels = LLMModels.GPT4o, cache_dir: str = './models', low_vram: bool = False):
        load_dotenv()
        self.model_id = model_id.value
        self.cache_dir = cache_dir
        self.chat_model = self._load_chat_model(model_id, low_vram)

    def _load_chat_model(self, model_id: LLMModels, low_vram: bool) -> Union[ChatOpenAI, HuggingFacePipeline]:
        if model_id == LLMModels.GPT4o:
            return ChatOpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.8,
                model_name=model_id.value
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
    

    def generate_video_script(self, content: str, words_number: int = 100) -> str:
        template = ChatPromptTemplate.from_messages([
            ("system", prompts.Prompts.ESP.GUION_VIDEO_VIRAL),
            ("human", "Escribe el script para un video sobre {content}. {output_format}"),
        ])

        output_format = prompts.OutputFormats.ESP.NUMERO_PALABRAS + prompts.OutputFormats.ESP.SIN_SALTOS_DE_LINEA
        output_format = output_format.format(words_number=words_number)

        messages = template.format_messages(
            output_format=output_format,
            content=content,
        )

        output = self.chat_model(messages)

        return output.content
    
    def split_text(self, text: str) -> List[str]:
        template = ChatPromptTemplate.from_messages([
            ("system", 
                prompts.OutputFormats.ENG.SPLIT_TEXT_SCENES 
            ),
            ("human", "Transform this text: {text}. Return only an array [] do not whirte any aditional text."),
        ])

        messages = template.format_messages(text=text)

        output_parser = ListOfDictsOutputParser()
        output = self.chat_model(messages)
        text_splited = output_parser.parse(output.content)
        return text_splited
    
    def generate_storyboard(self, text: str) -> List[Scene]:
        template = ChatPromptTemplate.from_messages([
            ("system", 
                prompts.OutputFormats.ENG.GENERATE_STORYBOARD
            ),
            ("human", "Create a storyboard for this text: {text}. {output_format}"),
        ])

        messages = template.format_messages(
            text=text,
            output_format=prompts.OutputFormats.ENG.GENERATE_STORYBOARD_OUTPUT_FORMAT
        )

        output_parser = ListOfDictsOutputParser()
        output = self.chat_model(messages)
        storyboard = output_parser.parse(output.content)
        storyboard = [Scene(text=scene['text'], image=scene['image']) for scene in storyboard]
        return storyboard