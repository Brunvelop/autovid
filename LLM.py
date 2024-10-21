import os
from dotenv import load_dotenv
from anthropic import Anthropic

from definitions import LLMModels

load_dotenv()
class AnthropicHandler:
    def __init__(self, model: LLMModels, llm_config: dict = {'max_tokens':1000}):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model.value
        self.llm_config = llm_config

    def generate_text(self, prompt):
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.llm_config.get('max_tokens',1000),
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

if __name__ == "__main__":
    # Initialize the AnthropicHandler with a specific model
    handler = AnthropicHandler(LLMModels.CLAUDE_3_5_sonnet)

    # Test prompt
    test_prompt = "What is the capital of France?"

    # Generate text using the handler
    response = handler.generate_text(test_prompt)

    # Print the response
    if response:
        print("Generated response:")
        print(response)
    else:
        print("Failed to generate a response.")
