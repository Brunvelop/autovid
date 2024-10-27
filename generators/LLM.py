import os
from enum import Enum
from dotenv import load_dotenv
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import cohere
from anthropic import Anthropic
from openai import OpenAI

load_dotenv()

class Models:
    #https://openai.com/api/pricing/
    class OpenAI(Enum):
        GPT4o = {
            'name': 'gpt-4o',
            'llm_config': {'max_tokens':16384 , 'temperature': 0},
            'input_cost': 2.5/10**6,  # $3 / MTok
            'output_cost': 10/10**6  # $15 / MTok
        }
        GPT4oMini = {
            'name': 'gpt-4o-mini',
            'llm_config': {'max_tokens':16384 , 'temperature': 0},
            'input_cost': 0.15/10**6,  # $0.15 / MTok
            'output_cost': 0.6/10**6  # $0.6 / MTok
        }

    #https://www.anthropic.com/pricing#anthropic-api
    class Anthropic(Enum):
        CLAUDE_3_5_sonnet = {
            'name': 'claude-3-5-sonnet-20240620',
            'llm_config': {'max_tokens':8192, 'temperature': 0},
            'input_cost': 3/10**6,  # $3 / MTok
            'output_cost': 15/10**6,  # $15 / MTok
        }
    
    class Cohere(Enum):
        COMMAND_R_PLUS = {
            'name': 'command-r-plus-08-2024',
            'llm_config': {'max_tokens': 4096, 'temperature': 0.3},
            'input_cost': 2.5/10**6,
            'output_cost': 10/10**6  
        }

    class Local(Enum):
        LLAMA31_8B = 'meta-llama/Meta-Llama-3.1-8B-Instruct'

@dataclass
class LLMResponse:
    text: str
    usage: int
    cost: float

class LLM(ABC):
    def __new__(cls, model: Models, llm_config: dict = None):
        if cls is LLM:
            if isinstance(model, Models.Anthropic):
                return super().__new__(AnthropicHandler)
            if isinstance(model, Models.OpenAI):
                return super().__new__(OpenAIHandler)
            if isinstance(model, Models.Cohere):
                return super().__new__(CohereHandler)
            else:
                raise ValueError(f"Unsupported model: {model}")
        return super().__new__(cls)

    def __init__(self, model: Models, llm_config: dict = None):
        self.model = model
        self.llm_config = llm_config

    @abstractmethod
    def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        prefill: Optional[str] = None
    ) -> Optional[LLMResponse]:
        pass

class AnthropicHandler(LLM):
    def __init__(self, model: Models.Anthropic, llm_config: dict = None):
        self.model = model
        self.llm_config = {**model.value.get('llm_config', {}), **(llm_config or {})}
        self.client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Optional[LLMResponse]:
        try:
            message = self._create_message(prompt, system_prompt, prefill)
            return LLMResponse(
                text=(prefill or '') + message.content[0].text,
                usage=message.usage.input_tokens + message.usage.output_tokens,
                cost=self._calculate_cost(message)
            )
        except Exception as e:
            print(f'An error occurred: {e}')
            return None

    def _create_message(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Any:
        params = {
            "model": self.model.value['name'],
            "messages": [
                {"role": "user", "content": prompt},
            ] + ([{"role": "assistant", "content": prefill}] if prefill else []),
            **({'system': system_prompt} if system_prompt else {}),
            **self.llm_config
        }
        return self.client.messages.create(**params)

    def _calculate_cost(self, message: Any) -> tuple[int, float]:
        model_costs = getattr(Models.Anthropic, self.model.name).value
        cost_input = message.usage.input_tokens * model_costs['input_cost']
        cost_output = message.usage.output_tokens * model_costs['output_cost']
        return cost_input + cost_output
    
class OpenAIHandler(LLM):
    def __init__(self, model: Models.OpenAI, llm_config: dict = None):
        self.model = model
        self.llm_config = {**model.value.get('llm_config', {}), **(llm_config or {})}
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Optional[LLMResponse]:
        try:
            message = self._create_message(prompt, system_prompt, prefill)
            return LLMResponse(
                text=message.choices[0].message.content,
                usage=message.usage.prompt_tokens + message.usage.completion_tokens,
                cost=self._calculate_cost(message)
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _create_message(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Any:
        params = {
            "model": self.model.value['name'],
            "messages": (
                ([{"role": "system", "content": system_prompt}] if system_prompt else []) +
                [{"role": "user", "content": prompt}] +
                ([{"role": "assistant", "content": prefill}] if prefill else [])
            ),
            **self.llm_config
        }
        return self.client.chat.completions.create(**params)

    def _calculate_cost(self, message: Any) -> tuple[int, float]:
        model_costs = getattr(Models.OpenAI, self.model.name).value
        input_cost = message.usage.prompt_tokens * model_costs['input_cost']
        output_cost = message.usage.completion_tokens * model_costs['output_cost']
        return input_cost + output_cost

class CohereHandler(LLM):
    def __init__(self, model: Models.Cohere, llm_config: dict = None):
        self.model = model
        self.llm_config = {**model.value.get('llm_config', {}), **(llm_config or {})}
        self.client = cohere.ClientV2(api_key=os.environ.get("COHERE_API_KEY"))

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Optional[LLMResponse]:
        try:
            message = self._create_message(prompt, system_prompt, prefill)
            return LLMResponse(
                text=message.message.content[0].text,
                usage=message.usage.tokens.input_tokens + message.usage.tokens.output_tokens,
                cost=self._calculate_cost(message)
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _create_message(self, prompt: str, system_prompt: Optional[str] = None, prefill: Optional[str] = None) -> Any:
        params = {
            "model": self.model.value['name'],
            "messages": (
                ([{"role": "system", "content": system_prompt}] if system_prompt else []) +
                [{"role": "user", "content": prompt}] +
                ([{"role": "assistant", "content": prefill}] if prefill else [])
            ),
            **self.llm_config
        }
        return self.client.chat(**params)

    def _calculate_cost(self, message: Any) -> tuple[int, float]:
        model_costs = getattr(Models.Cohere, self.model.name).value
        input_cost = message.usage.tokens.input_tokens * model_costs['input_cost']
        output_cost = message.usage.tokens.output_tokens * model_costs['output_cost']
        return input_cost + output_cost

if __name__ == "__main__":

    # Initialize both handlers
    anthropic_handler = LLM(model=Models.Anthropic.CLAUDE_3_5_sonnet)
    openai_handler = LLM(model=Models.OpenAI.GPT4o)

    # Test prompt and system prompt
    test_prompt = "Escribe una lista del 1 al 5"
    test_system_prompt = "Solo devuelves estructuras de datos evaluables en python"
    prefill = "["
    
    # Generate text with Anthropic
    print("Anthropic Response:")
    anthropic_result = anthropic_handler.generate_text(test_prompt, system_prompt=test_system_prompt, prefill=prefill)
    if anthropic_result:
        print("Generated Text:")
        print(anthropic_result.text)
        print(f"\nToken Usage: {anthropic_result.usage}")
        print(f"Estimated Cost: ${anthropic_result.cost:.6f}")
    else:
        print("Failed to generate text with Anthropic.")

    print("\n" + "="*50 + "\n")

    # Generate text with OpenAI
    print("OpenAI Response:")
    openai_result = openai_handler.generate_text(test_prompt, system_prompt=test_system_prompt, prefill=prefill)
    if openai_result:
        print("Generated Text:")
        print(openai_result.text)
        print(f"\nToken Usage: {openai_result.usage}")
        print(f"Estimated Cost: ${openai_result.cost:.6f}")
    else:
        print("Failed to generate text with OpenAI.")

    # Compare results
    if anthropic_result and openai_result:
        print("\nComparison:")
        print(f"Anthropic tokens: {anthropic_result.usage}, cost: ${anthropic_result.cost:.6f}")
        print(f"OpenAI tokens: {openai_result.usage}, cost: ${openai_result.cost:.6f}")
