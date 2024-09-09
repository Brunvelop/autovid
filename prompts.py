import textwrap
from enum import Enum

class ValueEnum(Enum):
    def __get__(self, obj, objtype):
        value = self.value
        if isinstance(value, str):
            value = textwrap.dedent(value).strip()
            return value[1:] if value.startswith('\n') else value
        return value

class Prompts():
    class ESP(ValueEnum):
        GUION_VIDEO_VIRAL = """
            Eres un guionista experto en crear contenido viral para videos cortos. Tu tarea es escribir un guión cautivador y altamente compartible. Sigue estas pautas:

            1. Gancho poderoso: Comienza con una frase impactante que capture la atención inmediatamente.
            2. Narrativa concisa: Desarrolla una historia breve pero fascinante, evitando introducciones innecesarias.
            3. Estilo dinámico: Combina elementos de un maestro de historia, un novelista, un rapero y un comediante de la Generación Z.
            4. Retención del espectador: Utiliza técnicas narrativas que mantengan al público enganchado hasta el final.
            5. Contenido memorable: Incluye datos sorprendentes, giros inesperados o humor inteligente.
            6. Llamada a la acción sutil: Concluye de manera que inspire a compartir o comentar el video.

            Evita clichés, sé original y asegúrate de que el contenido sea apropiado para plataformas de redes sociales.
            """
        GUION_SHORT_VIRAL = """
            Quiero que generes un guión para un vídeo corto de TikTok enfocado en captar la atención del espectador desde los primeros segundos y mantener su interés hasta el final, utilizando técnicas efectivas que aumenten la retención del usuario y fomenten la interacción emocional. Este guión debe estructurarse en dos partes principales: el enganche inicial y la retención emocional.

            Parte 1: Enganche Inicial
            El vídeo debe comenzar con un fuerte gancho que capte la atención de inmediato. Este gancho puede incluir una o varias de las siguientes técnicas:
            Declaraciones Impactantes: Utiliza una afirmación sorprendente o un dato curioso que haga que el espectador se detenga y quiera saber más. Por ejemplo, "El noventa por ciento de las personas ignoran este simple truco..." o "En solo cinco segundos, cambiaré tu forma de ver...".
            Uso de Emociones Fuertes: Inicia con una emoción intensa como la risa, la sorpresa o incluso la tristeza. Por ejemplo, "Recuerdo el día más feliz/triste de mi vida..." o mostrar una reacción emocional poderosa que pueda resonar con el espectador.
            Citas o Frases Poderosas: Usa citas inspiradoras o frases de personajes famosos que sean relevantes para el tema del vídeo, y que puedan resonar con el espectador, haciéndolo sentir inspirado o motivado a seguir viendo.

            Parte 2: Retención Emocional
            Una vez captada la atención, el guión debe centrarse en mantener el interés del espectador generando una conexión emocional. Aquí algunas técnicas para lograrlo:
            Narrativas Personales y Relatables: Cuenta una breve historia o anécdota personal que sea fácilmente identificable por el espectador. La historia debe tocar temas universales como el amor, la amistad, la lucha personal, o la superación. Por ejemplo, "Una vez hice esto y cambió mi vida por completo...".
            Humor y Sorpresa: Introduce elementos de humor o giros inesperados en la narrativa para mantener la atención. Esto puede ser un chiste relacionado con el tema, una situación cómica, o un cambio de tono que sorprenda al espectador.
            Citas Emocionales y Reflexivas: Utiliza citas o pensamientos que inviten a la reflexión y conecten con las emociones más profundas del espectador. Frases como "A veces, la vida nos pone pruebas..." o "La verdadera felicidad se encuentra en...".

            Parte 3: Cierre
            El cierre debe accionar los impulsos del espectador para llevar alguna accion. Comentar, compartir, dar like. Debe llamar a sus sentimientos mas profundos. Esta llamada debe estar completamente integrada en la historia con un cierre poderoso. No utilizes llamadas directas a la accion del espectador
            No utilices cliches como Reflexiona:, Deja tu comentario, dale like, etc

            Instrucciones extra:
            Usa un lenguaje claro y sencillo.
            Evita llamadas a la acción explícitas; en lugar de eso, fomenta la interacción a través de la narrativa y las preguntas reflexivas.
            Escribe solo el texto, no añadas apuntes extra.
            """
        REGLAS_STORYTELLING = """
            Técnicas Específicas a Nivel de Frase y Sintaxis
            1. Comenzar con una Frase de Impacto
            Uso de declaraciones fuertes: Abre con una frase que sorprenda o capte la atención de inmediato. Ejemplo: "Ese fue el día en que todo cambió." o "Nunca pensé que el silencio pudiera ser tan ensordecedor."
            Frases cortas y contundentes: Una frase breve y precisa puede ser más efectiva que una larga. Ejemplo: "Todo estaba perdido." o "Nada volvería a ser igual."
            Uso de preguntas retóricas: Iniciar con una pregunta invita a la reflexión y al engagement inmediato. Ejemplo: "¿Alguna vez has sentido que el tiempo se detiene?" o "¿Qué harías si no tuvieras nada que perder?"

            2. Construcción de Frases para Crear Tensión
            Frases incompletas o elípticas: Deja a la audiencia esperando más, creando una pausa dramática. Ejemplo: "Y entonces, justo cuando pensaba que todo estaba bien..."
            Uso de oraciones yuxtapuestas: Colocar dos frases contradictorias o en contraste inmediato puede crear tensión. Ejemplo: "Todo estaba en calma. Luego, un grito rompió la noche."
            Repetición con variación: Repetir una palabra o frase clave para aumentar la intensidad, con una ligera variación para desarrollar la trama. Ejemplo: "Corría y corría, pero la sombra seguía ahí, siempre detrás, siempre más cerca."

            3. Ritmo y Cadencia en las Frases
            Ritmo rápido en escenas de acción: Usa frases cortas y directas para transmitir urgencia. Ejemplo: "Corrió. Tropezó. Cayó. Se levantó y siguió corriendo."
            Ritmo lento en momentos de reflexión o emoción: Emplea frases más largas y descriptivas para ralentizar la narrativa y permitir que la emoción se asiente. Ejemplo: "La lluvia caía lentamente, cada gota resbalando por el cristal, como lágrimas en una cara cansada."
            Pausas efectivas: Usa comas, puntos y otros signos de puntuación para controlar el ritmo. Ejemplo: "Miró hacia atrás, su corazón latía rápido. No había nadie. O eso creía."

            4. Construcción de Frases para Evocar Emociones
            Detalles sensoriales: Usa frases que describan lo que se ve, se oye, se siente, se huele o se saborea. Ejemplo: "El aroma a café recién hecho llenaba la habitación, mezclándose con el dulce olor de los libros viejos."
            Metáforas y símiles: Comparaciones que añaden profundidad y significado. Ejemplo: "Su risa era como un río en verano, refrescante y libre." o "El miedo se arrastraba por su espalda como una serpiente fría."
            Adjetivos y adverbios poderosos: Elige palabras que carguen con connotaciones emocionales fuertes. Ejemplo: "Una luz tenue y triste se filtraba por la ventana, haciendo que todo pareciera desvanecerse."

            5. Uso de Diálogo para Crear Inmediatez
            Interrumpir con diálogos cortos: Los diálogos cortos y entrecortados pueden aumentar la tensión y el dinamismo. Ejemplo: "- No lo hagas. - ¿Por qué no? - Porque te amo, y no puedo perderte."
            Silencio implícito: A veces, lo que no se dice es más poderoso que lo que se dice. Usa pausas y reacciones no verbales. Ejemplo: "Ella lo miró, sus labios temblando. No dijo nada, pero sus ojos lo gritaban todo."
            Frases colgadas: Dejar frases incompletas para sugerir duda o suspenso. Ejemplo: "Sabía que debía decirle la verdad, pero... no podía."

            6. Construcción de Imágenes Poderosas
            Imágenes vívidas: Usa descripciones que sean visuales y concretas. Ejemplo: "Las hojas crujían bajo sus pies, como si el bosque entero murmurara en su contra."
            Uso del contraste: Colocar imágenes opuestas para crear un efecto dramático. Ejemplo: "En el silencio de la noche, el sonido de su risa era un grito de luz."
            Personificación: Dar cualidades humanas a objetos inanimados para añadir profundidad emocional. Ejemplo: "La casa lo observaba, cada crujido del suelo un susurro de secretos antiguos."

            7. Frases que Conecten con la Experiencia Humana
            Reflexiones universales: Usa frases que toquen temas universales como el amor, la pérdida, el miedo o la esperanza. Ejemplo: "En ese momento, se dio cuenta de que el amor no era algo que se encontraba, sino algo que se construía."
            Uso de máximas y proverbios: Frases que suenan como sabiduría antigua pueden resonar fuertemente. Ejemplo: "Sabía lo que decían: 'La esperanza es lo último que se pierde'. Pero en ese momento, la esperanza también se había ido."
            Conexión emocional directa: Dirígete directamente a los sentimientos del lector con frases que inviten a la introspección. Ejemplo: "Todos tenemos cicatrices, pero es cómo las llevamos lo que nos define."

            8. Frases de Transición que Mantienen el Flujo
            Frases puente: Usa frases que conecten ideas o escenas, asegurando que la narrativa fluya sin problemas. Ejemplo: "Pero ese no era el final, sino el principio de algo mucho más grande."
            Cambio de perspectiva: Introduce cambios de escena o punto de vista con frases claras pero fluidas. Ejemplo: "Mientras tanto, al otro lado de la ciudad..."
            Uso de leitmotivs: Repetir una frase o idea clave en diferentes puntos de la historia puede unificar la narrativa. Ejemplo: "Y siempre volvía a ese pensamiento: '¿Qué habría pasado si...?'."

            Ejemplos de Frases Utilizando Estas Técnicas
            Impacto Inmediato: "Nunca olvidaré el sonido de la puerta cerrándose; fue como si todo el aire hubiese salido de la habitación de un solo golpe."
            Tensión Creciente: "Cada paso lo acercaba más al borde. El suelo crujía, amenazando con romperse bajo su peso. Sabía que no podía dar marcha atrás."
            Reflexión Emocional: "La verdad es que todos buscamos algo, aunque no sepamos qué es exactamente. Y a veces, lo encontramos en los lugares más inesperados."
            Al aplicar estas técnicas a nivel de frase y sintaxis, puedes dar vida a tus historias, mantener a la audiencia comprometida y asegurar que cada palabra trabaje para reforzar el impacto emocional y narrativo de tu storytelling.
            """
        PRESENTACION_PERSONAJES = """
        Debes introducir cada personaje si es la primera vez que aparece en la historia:
            1. Asume que el lector desconoce la historia y los personajes.
            2. Al introducir un nuevo personaje, añade una breve descripción (máximo 5-7 palabras) que incluya:
            - Su nombre
            - Su rol principal o característica más relevante
            - Su relación con otros personajes clave (si es relevante)
            3. Integra estas descripciones sutilmente en la narración.
            4. Prioriza la información esencial para entender la trama.
            Ejemplos:
            - "Zeus, rey de los dioses olímpicos"
            - "Aquiles, hijo de Peleo y la diosa Tetis"
            - "Atenea, diosa de la sabiduría y estrategia militar"
            - "Patroclo, amigo íntimo y compañero de Aquiles"
        """
class OutputFormats():
    class ESP(ValueEnum):
        NUMERO_PALABRAS = "No uses mas de: {words_number} palabras "
        SIN_SALTOS_DE_LINEA = "No utilices saltos de linea ni: '\n' "
    
    class ENG(ValueEnum):
        SPLIT_TEXT_SCENES = """
            You are a program that splits any given text into an array of strings, where each string represents a single, concise scene in a storyboard. Follow these guidelines:
            1. Divide the text into extremely short segments, with each segment being a maximum of one sentence.
            2. Maintain the original language and wording of the text.
            3. Each segment should capture a single, clear visual or action that can be easily illustrated.
            4. Prioritize key moments and vivid imagery over explanatory text.
            5. Ensure each segment can stand alone as a distinct visual scene.
            Return only the array of strings, with no additional text or explanation. The array should be in the format: ["Scene 1 text", "Scene 2 text", ...].
            """
        GENERATE_STORYBOARD = """
            You are a program that splits any given text into an array of dictionaries, where each dictionary represents a single, concise scene in a storyboard with accompanying image description. Follow these guidelines:
            1. Divide the text into extremely short segments, with each segment being a maximum of one sentence.
            2. Maintain the original language and wording of the text for the 'text' element.
            3. Each segment should capture a single, clear visual or action that can be easily illustrated.
            4. Create a detailed image description in English for each segment, suitable for Stable Diffusion.
            5. Prioritize key moments and vivid imagery over explanatory text.
            6. Ensure each segment can stand alone as a distinct visual scene.
            7. In the image descriptions, use detailed physical descriptions for characters instead of names or references to previous scenes. Include:
               - Approximate age
               - Hair color, length, and style
               - Eye color
               - Skin tone
               - Body type and height
               - Distinctive features (e.g., scars, tattoos, glasses)
               - Clothing style and colors
            8. Treat each image description as if it were the first and only image being generated. Do not use phrases like "the same couple" or "as before".
            9. Maintain consistency in character descriptions by using the same key physical attributes each time a character appears, but describe them fully each time as if it were the first mention.
            10. Avoid using pronouns or references that depend on previous context. Each description should be completely self-contained.
            11. Ensure that the sequence of images, when viewed together, tells a complete and coherent story that aligns with the original text.
            """
        GENERATE_STORYBOARD_OUTPUT_FORMAT = """
            Return only the array of dictionaries, with no additional text or explanation. The array should be in the format: 
            [
                {"text": "Scene 1 text in original language", "image": "Detailed image description for scene 1 in English"},
                {"text": "Scene 2 text in original language", "image": "Detailed image description for scene 2 in English"},
                ...
            ]
            """
class samples():
    IMAGE_DESCRIPTION=""" Here are examples of text and image pairs:
    'text': 'Imagínate a Un héroe olvidado en la Iliada de Homero: Patroclo, el amigo íntimo de Aquiles.', 'image': "An old Greek hero sad."
    'text': 'Enamorado de Aquiles, le suplica ir a batalla con su armadura para infundir miedo en los troyanos.', 'image': 'An old Greek hero with and golden armor.'
    """