from typing import Dict
from pathlib import Path

from prompts import OutputFormats, WriterPrompts
from LLM import LLM

# Evaluation prompts
HISTORICAL_ACCURACY_PROMPT = """
Eres un historiador experto. Tu tarea es evaluar la precisión histórica del texto proporcionado.
Analiza cuidadosamente el contenido y determina si es históricamente preciso o no.
Responde únicamente con True si el texto es históricamente preciso, o False si contiene inexactitudes históricas.
"""

STORYTELLING_QUALITY_PROMPT = """
Eres un experto en narrativa y storytelling. Tu tarea es evaluar la calidad narrativa del texto proporcionado.
Analiza el texto considerando elementos como la estructura, el desarrollo de personajes, el arco narrativo y el engagement.
Califica la calidad del storytelling en una escala del 1 al 10, donde 1 es muy pobre y 10 es excelente.
Responde únicamente con un número del 1 al 10.
"""

EMOTIONAL_IMPACT_PROMPT = """
Eres un psicólogo especializado en el impacto emocional de la narrativa. Tu tarea es evaluar el impacto emocional del texto proporcionado.
Analiza el texto considerando su capacidad para evocar emociones, crear conexiones empáticas y dejar una impresión duradera en el lector.
Califica el impacto emocional en una escala del 1 al 10, donde 1 es nulo impacto y 10 es impacto extremadamente fuerte.
Responde únicamente con un número del 1 al 10.
"""

class Writer():
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def generate_story(self, content: str, words_number: int = 100) -> str:
        text = self.llm.generate_text(
            system_prompt=WriterPrompts.REGLAS_STORYTELLING,
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
            "historical_accuracy": self._evaluate_aspect(text, HISTORICAL_ACCURACY_PROMPT, lambda x: x.strip().lower() == 'true'),
            "storytelling_quality": self._evaluate_aspect(text, STORYTELLING_QUALITY_PROMPT, lambda x: int(x.strip())),
            "emotional_impact": self._evaluate_aspect(text, EMOTIONAL_IMPACT_PROMPT, lambda x: int(x.strip()))
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
    print(f"Characters: {len(text)}")
    writer.save_text(
        text=text,
        save_path=Path(f'data/MITO_TV/SHORTS/MITOS_NORDICOS/{N}/text/text.txt')
    )

    # Example usage of the new evaluate_text function
    evaluations = writer.evaluate_text(text)
    print("\nEvaluaciones del texto:")
    for aspect, value in evaluations.items():
        print(f"{aspect.replace('_', ' ').title()}: {value}")