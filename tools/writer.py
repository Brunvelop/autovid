import sys, os
if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import statistics
from typing import Dict
from pathlib import Path

from prompts import WriterPrompts
from generators.LLM import LLM, LLMResponse

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm
        
    def generate_story(self, expertise: str, theme: str, words_number: int = 100) -> Dict[str, any]:
        output: LLMResponse = self.llm.generate_text(
            system_prompt=WriterPrompts.System.scriptwriter(expertise=expertise),
            prompt=WriterPrompts.User.short_text_generator(
                theme=theme,
                words_number=words_number
            )
        )
        return {
            'text': self._clean_text(output.extract_tag('text')),
            'full_output': output.text,
            'cost': output.cost
        }
    
    def improve_story(self, expertise: str, text: str, words_number: int = 100) -> Dict[str, any]:
        output: LLMResponse = self.llm.generate_text(
            system_prompt=WriterPrompts.System.scriptwriter(expertise=expertise),
            prompt=WriterPrompts.User.short_text_improver(
                text=text,
                words_number=words_number
            )
        )
        return {
            'text': self._clean_text(output.extract_tag('texto_mejorado')),
            'full_output': output.text,
            'cost': output.cost
        }
    
    def generate_theme(self, used_themes: str, expertise: str, serie_theme: str) -> Dict[str, any]:
        output = self.llm.generate_text(
            system_prompt=f'Eres un experto en elegir temas para textos de {expertise}',
            prompt=f"{used_themes} No puedes repetir los temas de memoria, elige un nuevo tema relacionado con: {serie_theme}, escribe solo el tema en pocas palabras"
        )
        return {
            'text': self._clean_text(output.text),
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
        scores = {
            "historical_accuracy": self._evaluate_aspect(text, WriterPrompts.Evaluation.evaluate_historical_accuracy(), lambda x: float(x.strip())),
            "storytelling_quality": self._evaluate_aspect(text, WriterPrompts.Evaluation.evaluate_storytelling(), lambda x: float(x.strip())),
            "emotional_impact": self._evaluate_aspect(text, WriterPrompts.Evaluation.evaluate_emotional_impact(), lambda x: float(x.strip())),
            "average_score": None,
            "word_count": len(text.split())
        }
        scores["average_score"] = statistics.mean([v for k,v in scores.items() if k not in ["average_score", "word_count"]])
        return scores

    def _evaluate_aspect(self, text: str, prompt: str, parse_function: callable) -> any:
        result: LLMResponse = self.llm.generate_text(
            system_prompt=prompt,
            prompt=f"Evalúa el siguiente texto:\n\n{text}",
        )
        return parse_function(result.text)

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
