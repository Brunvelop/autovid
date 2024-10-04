from typing import Dict, Tuple
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
            "historical_accuracy": self._evaluate_aspect(text, WriterPrompts.Evaluation.HISTORICAL_ACCURACY, lambda x: int(x.strip())),
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

    def improve_text(self, text: str, depth: int = 3) -> Tuple[str, Dict[str, list]]:
        improvements = {
            "historical_accuracy": [],
            "storytelling_quality": [],
            "emotional_impact": []
        }
        
        for _ in range(depth):
            evaluation = self.evaluate_text(text)
            
            # Determine which aspect to improve based on the evaluation
            aspect_to_improve = min(evaluation, key=lambda k: evaluation[k] if k != "word_count" else float('inf'))
            
            if aspect_to_improve == "historical_accuracy":
                prompt = WriterPrompts.Improvement.HISTORICAL_ACCURACY
            elif aspect_to_improve == "storytelling_quality":
                prompt = WriterPrompts.Improvement.STORYTELLING_QUALITY
            elif aspect_to_improve == "emotional_impact":
                prompt = WriterPrompts.Improvement.EMOTIONAL_IMPACT
            else:
                break  # No more improvements needed
            
            improved_text, summary = self._improve_aspect(text, prompt)
            improvements[aspect_to_improve].append(summary)
            
            text = improved_text
            
            # Check if we've reached our objectives
            if all(evaluation[k] >= 10 for k in ["storytelling_quality", "emotional_impact"]) and evaluation["historical_accuracy"]:
                break
        
        return text, improvements

    def _improve_aspect(self, text: str, prompt: str) -> Tuple[str, str]:
        result = self.llm.generate_text(
            system_prompt=prompt,
            human_prompt=f"Mejora el siguiente texto:\n\n{text}"
        )
        
        improved_text = self._extract_content(result, "improved_text")
        summary = self._extract_content(result, "summary")
        
        return improved_text.strip(), summary.strip()
    
    @staticmethod
    def _extract_content(text: str, tag: str) -> str:
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = text.find(start_tag) + len(start_tag)
        end = text.find(end_tag)
        return text[start:end].strip()

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
    print("\n" + "=" * 50)
    print("Texto original".center(50))
    print("=" * 50)
    print(text)
    
    evaluations = writer.evaluate_text(text)
    print("\nEvaluaciones del texto original:")
    print("-" * 30)
    for aspect, value in evaluations.items():
        print(f"{aspect.replace('_', ' ').title():<30}: {value}")
    
    improved_text, improvements = writer.improve_text(text, depth=5)
    print("\n" + "=" * 50)
    print("Texto mejorado".center(50))
    print("=" * 50)
    print(improved_text)
    
    print("\nResumen de las mejoras:")
    print("-" * 30)
    for aspect, summaries in improvements.items():
        print(f"\n{aspect.replace('_', ' ').title()}:")
        for i, summary in enumerate(summaries, 1):
            print(f"  Iteración {i}: {summary}")
    
    improved_evaluations = writer.evaluate_text(improved_text)
    print("\nEvaluaciones del texto mejorado:")
    print("-" * 30)
    for aspect, value in improved_evaluations.items():
        print(f"{aspect.replace('_', ' ').title():<30}: {value}")
