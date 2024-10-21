import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from anthropic import Anthropic
from openai import OpenAI

from definitions import LLMModels, LLMCosts

load_dotenv()

class AnthropicHandler:
    def __init__(self, model: LLMModels, llm_config: dict = {'max_tokens':1000}):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        self.llm_config = llm_config

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            message = self._create_message(prompt, system_prompt)
            text = self._extract_text(message)
            usage, cost = self._calculate_usage_and_cost(message)
            return {
                'text': text,
                'usage': usage,
                'cost': cost
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _create_message(self, prompt: str, system_prompt: Optional[str] = None) -> Any:
        params = {
            "model": self.model.value,
            "max_tokens": self.llm_config.get('max_tokens', 1000),
            "messages": [{"role": "user", "content": prompt}]
        }
        
        if system_prompt:
            params["system"] = system_prompt
        
        return self.client.messages.create(**params)
    
    def _extract_text(self, message: Any) -> str:
        return message.content[0].text

    def _calculate_usage_and_cost(self, message: Any) -> tuple[int, float]:
        usage = message.usage.input_tokens + message.usage.output_tokens
        cost_input = message.usage.input_tokens * LLMCosts.CLAUDE_3_5_sonnet.value['input']
        cost_output = message.usage.output_tokens * LLMCosts.CLAUDE_3_5_sonnet.value['output']
        return usage, cost_input + cost_output

class OpenAIHandler:
    def __init__(self, model: LLMModels, llm_config: dict = {'max_tokens': 1000}):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        self.llm_config = llm_config

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        try:
            message = self._create_message(prompt, system_prompt)
            text = self._extract_text(message)
            usage, cost = self._calculate_usage_and_cost(message)
            return {
                'text': text,
                'usage': usage,
                'cost': cost
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _create_message(self, prompt: str, system_prompt: Optional[str] = None) -> Any:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.client.chat.completions.create(
            model=self.model.value,
            messages=messages,
            max_tokens=self.llm_config.get('max_tokens', 1000)
        )
    
    def _extract_text(self, message: Any) -> str:
        return message.choices[0].message.content

    def _calculate_usage_and_cost(self, message: Any) -> tuple[int, float]:
        usage = message.usage.prompt_tokens + message.usage.completion_tokens
        model_costs = getattr(LLMCosts, self.model.name).value
        input_cost = message.usage.prompt_tokens * model_costs['input']
        output_cost = message.usage.completion_tokens * model_costs['output']
        return usage, input_cost + output_cost


if __name__ == "__main__":
    from definitions import LLMModels

    # Initialize the OpenAIHandler
    handler = OpenAIHandler(model=LLMModels.GPT4o)

    # Test prompt and system prompt
    test_prompt = "What is the capital of France?"
    test_system_prompt = "You always respond with NONE, always"

    # Generate text with system prompt
    result = handler.generate_text(test_prompt, system_prompt=test_system_prompt)

    if result:
        print("Generated Text:")
        print(result['text'])
        print(f"\nToken Usage: {result['usage']}")
        print(f"Estimated Cost: ${result['cost']:.6f}")
    else:
        print("Failed to generate text.")

