from typing import Dict, Tuple
from pathlib import Path

from prompts import WriterPrompts
from generators.LLM import LLM, LLMResponse

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        
    def generate_story(self, expertise: str, theme: str, words_number: int = 100) -> Dict[str, any]:
        output: LLMResponse = self.llm.generate_text(
            system_prompt=WriterPrompts.System.THEME_WRITER.format(expertise=expertise),
            prompt=WriterPrompts.User.SHORTS_TEXT_GENERATOR.format(
                theme=theme,
                words_number=words_number
            )
        )
        return {
            'text': self._clean_text(self._extract_tag(output.text, 'text')),
            'full_output': output.text,
            'cost': output.cost
        }
    
    def improve_story(self, expertise: str, text: str, words_number: int = 100) -> Dict[str, any]:
        output: LLMResponse = self.llm.generate_text(
            system_prompt=WriterPrompts.System.THEME_WRITER.format(expertise=expertise),
            prompt=WriterPrompts.User.IMPROVE_CLARITY.format(
                text=text,
                words_number=words_number
            )
        )
        return {
            'text': self._clean_text(self._extract_tag(output.text, 'texto_mejorado')),
            'full_output': output.text,
            'cost': output.cost
        }
    
    def save_text(self, text: str, save_path: Path) -> None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(text, encoding='utf-8')

    def _clean_text(self, text):
        text = text.replace('"', "'")
        return text
    
    def evaluate_text(self, text: str) -> Dict[str, any]:
        evaluations = {
            "historical_accuracy": self._evaluate_aspect(text, WriterPrompts.Evaluation.HISTORICAL_ACCURACY, lambda x: int(x.strip())),
            "storytelling_quality": self._evaluate_aspect(text, WriterPrompts.Evaluation.STORYTELLING_QUALITY, lambda x: int(x.strip())),
            "emotional_impact": self._evaluate_aspect(text,  WriterPrompts.Evaluation.EMOTIONAL_IMPACT, lambda x: int(x.strip())),
            "word_count": len(text.split())
        }
        return evaluations

    def _evaluate_aspect(self, text: str, prompt: str, parse_function: callable) -> any:
        result: LLMResponse = self.llm.generate_text(
            system_prompt=prompt,
            prompt=f"Evalúa el siguiente texto:\n\n{text}",
        )
        return parse_function(result.text)
    
    @staticmethod
    def _extract_tag(text: str, tag: str) -> str:
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = text.find(start_tag) + len(start_tag)
        end = text.find(end_tag)
        return text[start:end].strip()

if __name__ == "__main__":
    from generators.LLM import Models
    
    writer = Writer(LLM(model=Models.OpenAI.GPT4oMini))

    story = writer.generate_story(
        expertise='Mitología Griega',
        theme='El origen de Zeus',
        words_number=100,
    )
    print(story['full_output'])

    print("\n ########################## \n")

    improved_story = writer.improve_story(
        expertise='Mitología Griega',
        text=story['text'],
        words_number=100,
    )
    print(improved_story['full_output'])
