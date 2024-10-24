from abc import ABC
from pathlib import Path

from generators.LLM import LLM
from prompts import WriterPrompts, OutputFormats

class Actions():
    GENERATE_HISTORY = ""

class Agent(ABC):
    def __init__(self, llm: LLM, memory_path: Path):
        self.llm = llm
        self.memory_path = memory_path
        self.memory: list = self._load_memory()

    def _load_memory(self) -> list:
        if self.memory_path.exists():
            memory = self.memory_path.read_text(encoding='utf-8')
            return self._memory_to_list(memory)
        else:
            return []

    def _save_memory(self) -> None:
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(self._memory_to_string(), encoding='utf-8')
    
    def _memory_to_list(self, memory: str) -> list:
        if memory.startswith("<memory>") and memory.endswith("</memory>"):
            memory = memory.strip("<memory></memory>")
            try:
                return eval(memory)
            except:
                return []
        return []

    def _memory_to_string(self) -> str:
        return f"<memory>{self.memory}</memory>"

    def _clean_text(self, text):
        text = text.replace('"', "'")
        return text

class ShortsWriter(Agent):
    def generate_serie(self):
        pass

    def _generate_story(self, content: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
            system_prompt=WriterPrompts.System.REGLAS_STORYTELLING,
            prompt = "\n".join([
                f"Utiliza el storytelling para escribir {content}",
                OutputFormats.SALTO_DE_LINEA_SIMPLE,
                OutputFormats.NUMERO_PALABRAS.format(words_number=words_number),
            ])
        )['text']
        return self._clean_text(text)
    
    def _generate_hook(self, content: str) -> str:
        text = self.llm.generate_text(
            system_prompt=WriterPrompts.System.HOOK,
            prompt= f"Crea un hook sobre: {content}"
        )['text']
        return self._clean_text(text)


if __name__ == '__main__':
    from generators.LLM import Models
    from pathlib import Path

    memory_path = Path('memory.txt')
    agent = Agent(LLM(model=Models.OpenAI.GPT4o), memory_path)

    # Test memory functionality
    print("Initial memory:", agent.memory)

    # Add some test data to memory
    agent.memory.append("Test memory item 1")
    agent.memory.append("Test memory item 2")
    
    print("Updated memory:", agent.memory)

    # Save memory
    agent._save_memory()
    print("Memory saved.")

    # Load memory
    loaded_agent = Agent(LLM(model=Models.OpenAI.GPT4o), memory_path)
    print("Loaded memory:", loaded_agent.memory)

    # Clean up: remove the test memory file
    memory_path.unlink()
    print("Test memory file removed.")
