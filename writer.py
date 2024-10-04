from typing import Dict
from pathlib import Path

from prompts import WriterPrompts
from LLM import LLM

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_story(self, content: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
            system_prompt=WriterPrompts.System.REGLAS_STORYTELLING,
            human_prompt=f"Utiliza el storytelling para escribir {content}",
            output_format= 
                WriterPrompts.OutputFormats.NUMERO_PALABRAS.format(words_number=words_number) +
                WriterPrompts.OutputFormats.SALTO_DE_LINEA_SIMPLE
        )
        text = text.replace('"', "'")
        return text
    
    def save_text(self, text: str, save_path: Path) -> None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(text, encoding='utf-8')

    def evaluate_text(self, text: str) -> Dict[str, any]:
        evaluations = {
            "historical_accuracy": self._evaluate_aspect(text, WriterPrompts.Evaluation.HISTORICAL_ACCURACY, lambda x: x.strip().lower() == 'true'),
            "storytelling_quality": self._evaluate_aspect(text, WriterPrompts.Evaluation.STORYTELLING_QUALITY, lambda x: int(x.strip())),
            "emotional_impact": self._evaluate_aspect(text,  WriterPrompts.Evaluation.EMOTIONAL_IMPACT, lambda x: int(x.strip())),
            "word_count": len(text.split())
        }
        return evaluations

    def _evaluate_aspect(self, text: str, prompt: str, parse_function: callable) -> any:
        result = self.llm.generate_text(
            system_prompt=prompt,
            human_prompt=f"Evalúa el siguiente texto:\n\n{text}",
            output_format="Responde únicamente con el formato especificado en las instrucciones."
        )
        return parse_function(result)

if __name__ == "__main__":
    from LLM import GPT4o, Claude35Sonnet
    
    N = 3
    writer = Writer(
        llm=Claude35Sonnet(
            low_vram=False,
            llm_config={
                'temperature': 0.5,
            }
        )
    )
    text = writer.generate_story(
        content='El mito nordico sobre El Árbol del Mundo Yggdrasil y los Nueve Mundos: Conexión de todos los reinos de la existencia.',
        words_number=120
    )
    print(text)
    evaluations = writer.evaluate_text(text)
    print("\nEvaluaciones del texto:")
    for aspect, value in evaluations.items():
        print(f"{aspect.replace('_', ' ').title()}: {value}")