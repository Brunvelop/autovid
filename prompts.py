import textwrap
from enum import Enum

class ValueEnum(Enum):
    def __get__(self, obj, objtype):
        value = self.value
        if isinstance(value, str):
            value = textwrap.dedent(value).strip()
            return value[1:] if value.startswith('\n') else value
        return value

class WriterPrompts(ValueEnum):
    REGLAS_STORYTELLING = """
        Técnicas de storytelling Específicas a Nivel de Frase y Sintaxis
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
    HOOK = """
        A partir del siguiente tema o texto, quiero que generes un hook de texto breve, de una sola frase, que capte la atención inmediata del lector y lo haga querer seguir leyendo. El hook debe sentirse como un "guantazo" de sorpresa, curiosidad o emoción, algo que interrumpa el flujo habitual de pensamiento y provoque una pausa en su atención. Debe basarse en el tema dado y reflejar una de estas estrategias:

        Disonancia cognitiva: Presenta una afirmación que desafíe las expectativas del lector o rompa la lógica común, generando una pausa inmediata en su pensamiento. El hook debe ser lo suficientemente inesperado para que el lector sienta la necesidad de entender más.

        Curiosidad sin respuesta inmediata: Plantea una pregunta o insinuación intrigante basada en el tema, dejando una incógnita que obligue al lector a seguir adelante. La clave es generar una sensación de misterio con pocas palabras.

        Vulnerabilidad emocional: Relaciona el tema con una emoción fuerte, como el miedo o el deseo. El hook debe conectar con una experiencia universal o una verdad emocional que haga que el lector sienta algo personal.

        Paradoja o contradicción: Utiliza una paradoja o contradicción clara que confunda momentáneamente al lector. La idea es provocar una fricción mental que lo invite a resolver el conflicto interno.

        Urgencia o inmediatez: Haz que el tema parezca urgente o esencial, jugando con el concepto de tiempo. El hook debe sugerir que algo importante está a punto de suceder o que el tiempo es crucial, para aumentar la atención inmediata.

        Recuerda que el hook debe ser directo, claro y no más largo de una frase, con el objetivo de generar un fuerte deseo de continuar la lectura. Mantén el contenido conciso y evita la verbosidad. Cada palabra cuenta y debe tener mucho impacto. Recerda usar muy pocas palabras, las minimas posibles
    """
    SALTO_DE_LINEA_SIMPLE = "Utiliza solo un salto de linea cuando sea necesario '\n'. No uses doble salto de linea "
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
            Técnicas de storytelling Específicas a Nivel de Frase y Sintaxis
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
    
    class Evaluation(ValueEnum):
        HISTORICAL_ACCURACY = """
            Eres un historiador experto. Tu tarea es evaluar la precisión histórica del texto proporcionado.
            Analiza cuidadosamente el contenido y determina si es históricamente preciso o no.
            Evalúa la precisión histórica del texto en una escala del 1 al 10, donde 1 es completamente inexacto y 10 es totalmente preciso históricamente. 
            Responde únicamente con un número del 1 al 10.
        """

        STORYTELLING_QUALITY = """
            Eres un experto en narrativa y storytelling. Tu tarea es evaluar la calidad narrativa del texto proporcionado.
            Analiza el texto considerando elementos como la estructura, el desarrollo de personajes, el arco narrativo y el engagement.
            Califica la calidad del storytelling en una escala del 1 al 10, donde 1 es muy pobre y 10 es excelente.
            Responde únicamente con un número del 1 al 10.
        """

        EMOTIONAL_IMPACT = """
            Eres un psicólogo especializado en el impacto emocional de la narrativa. Tu tarea es evaluar el impacto emocional del texto proporcionado.
            Analiza el texto considerando su capacidad para evocar emociones, crear conexiones empáticas y dejar una impresión duradera en el lector.
            Califica el impacto emocional en una escala del 1 al 10, donde 1 es nulo impacto y 10 es impacto extremadamente fuerte.
            Responde únicamente con un número del 1 al 10.
        """

    class Improvement(ValueEnum):
        HISTORICAL_ACCURACY = """
            Eres un historiador experto y escritor talentoso. Tu tarea es mejorar la precisión histórica del texto proporcionado sin perder su esencia narrativa y manteniendo un tamaño similar al original.
            Sigue estos pasos para analizar y mejorar el texto:

            <thinking>
            1. Lee cuidadosamente el texto proporcionado y anota su longitud aproximada.
            2. Identifica cualquier inexactitud histórica, anotando cada una.
            3. Investiga los hechos correctos para cada inexactitud identificada.
            4. Considera cómo corregir cada inexactitud mientras mantienes el tono, estilo original y longitud similar.
            5. Evalúa si las correcciones afectan otras partes del texto y ajusta en consecuencia.
            6. Revisa el texto completo para asegurar coherencia, fluidez y longitud similar después de las correcciones.
            </thinking>

            <improved_text>
            [Inserta aquí el texto mejorado, incorporando las correcciones históricas mientras mantienes el tono, estilo original y una longitud similar]
            </improved_text>

            <summary>
            [Proporciona un resumen de las mejoras realizadas, detallando cada inexactitud corregida y cómo se mejoró la precisión histórica, mencionando cómo se mantuvo una longitud similar]
            </summary>
        """

        STORYTELLING_QUALITY = """
            Eres un experto en narrativa y storytelling. Tu tarea es mejorar la calidad narrativa del texto proporcionado manteniendo una longitud similar al original.
            Sigue estos pasos para analizar y mejorar el texto:

            <thinking>
            1. Lee detenidamente el texto proporcionado y anota su longitud aproximada.
            2. Analiza la estructura actual de la narrativa.
            3. Evalúa el desarrollo de los personajes existentes.
            4. Examina el arco narrativo y su efectividad.
            5. Identifica áreas donde el engagement del lector puede mejorarse.
            6. Considera cómo mejorar cada aspecto manteniendo la esencia original y una longitud similar.
            7. Planifica las modificaciones para aumentar el interés del lector y la fluidez de la narración sin extender significativamente el texto.
            </thinking>

            <summary>
            [Proporciona un resumen de las mejoras realizadas, detallando cómo se ha mejorado la calidad narrativa en términos de estructura, personajes, arco narrativo y engagement, mencionando cómo se mantuvo una longitud similar]
            </summary>

            <improved_text>
            [Inserta aquí el texto mejorado, incorporando las mejoras en estructura, desarrollo de personajes, arco narrativo y engagement, manteniendo una longitud similar al original]
            </improved_text>
        """

        EMOTIONAL_IMPACT = """
            Eres un psicólogo especializado en el impacto emocional de la narrativa y un escritor talentoso. Tu tarea es mejorar el impacto emocional del texto proporcionado manteniendo una longitud similar al original.
            Sigue estos pasos para analizar y mejorar el texto:

            <thinking>
            1. Lee atentamente el texto proporcionado y anota su longitud aproximada.
            2. Identifica las emociones principales que el texto intenta evocar.
            3. Evalúa la efectividad actual del texto en evocar estas emociones.
            4. Analiza las conexiones empáticas existentes entre los personajes y el lector.
            5. Considera cómo intensificar la respuesta emocional sin cambiar drásticamente la trama, el tono o la longitud.
            6. Planifica modificaciones sutiles que aumenten el impacto emocional sin extender significativamente el texto.
            7. Revisa para asegurar que las mejoras creen una impresión duradera en el lector mientras mantienes una longitud similar.
            </thinking>

            <summary>
            [Proporciona un resumen de las mejoras realizadas, detallando cómo se ha intensificado el impacto emocional y las conexiones empáticas sin cambiar drásticamente la trama, el tono original o la longitud del texto]
            </summary>

            <improved_text>
            [Inserta aquí el texto mejorado, incorporando las mejoras para aumentar el impacto emocional y las conexiones empáticas, manteniendo una longitud similar al original]
            </improved_text>
        """
        
    class OutputFormats(ValueEnum):
        NUMERO_PALABRAS = "No uses mas de: {words_number} palabras "
        SIN_SALTOS_DE_LINEA = "No utilices saltos de linea ni: '\n' "
        SALTO_DE_LINEA_SIMPLE = "Utiliza solo un salto de linea cuando sea necesario '\n'. No uses doble salto de linea "


class StoryboarderPrompts:    
    class System(ValueEnum):
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
        GENERATE_TUMBNAIL = """
            Generate a detailed description for an artistic image that visually represents the given text. The image should creatively incorporate the original text within the scene. Follow these guidelines:

            1. Choose an appropriate artistic style for the theme (e.g., modern, classical, surrealist, etc.).
            2. Describe the main scene that captures the essence of the text.
            3. Include details about characters, their expressions, and actions.
            4. Describe the environment and atmosphere surrounding the scene.
            5. Specify how the original text is integrated into the image (e.g., formed by clouds, carved in stone, etc.).
            6. Use descriptive and vivid language to clearly convey the image.
            7. Keep the description concise yet detailed, ideally in a single paragraph.
            8. Do not include the original text in your response, only the image description.

            EXAMPLES:
            TEXT: '1. El Nacimiento de Afrodita'
            RESULT: A vibrant, modern art style painting of Aphrodite emerging from the ocean at sunrise, with the bold text '1. El Nacimiento de Afrodita' placed in the sky, formed by soft clouds, contrasting against the warm pink and orange tones of the horizon.

            TEXT: '2. El Sacrificio de Ifigenia.'
            RESULT: A dramatic, classical art style painting of the scene '2. El Sacrificio de Ifigenia.' In the foreground, Iphigenia stands gracefully before an altar, her expression calm yet somber. The altar is surrounded by priests in dark robes, while her father, Agamemnon, watches with a heavy heart. In the background, the sky is dark with swirling clouds, casting an ominous atmosphere over the scene. The bold text '2. El Sacrificio de Ifigenia' is written in the sky, formed by dark storm clouds, contrasting against the pale light breaking through in the distance.
            
            TEXT: '3. El Castigo de Tántalo.'
            RESULT: A haunting, surreal art style painting depicting the scene '3. El Castigo de Tántalo.' In the center, Tantalus stands waist-deep in a pool of water, reaching up toward a lush fruit tree that dangles its branches just out of his grasp. His expression is one of desperation and torment. The water below him recedes as he tries to drink, while the sky above is stormy and turbulent. The bold text '3. El Castigo de Tántalo' is formed by ghostly wisps of smoke rising from the ground, contrasting against the dark, ominous clouds rolling in the background.

            TEXT: '4. La Venganza de Medea.'
            RESULT: A dark, intense art style painting illustrating the scene '4. La Venganza de Medea.' In the foreground, Medea stands with a fierce, determined expression, holding a bloodied dagger. Behind her, the shadowy figures of her slain children lie on the ground, while flames rise in the distance, consuming the palace of Jason. Her flowing robes whip in the wind, blending with the smoke and fire. The bold text '4. La Venganza de Medea' is emblazoned in the sky, formed by fiery embers and smoke, contrasting against the night sky filled with swirling dark clouds.

            TEXT: '5. El Destino de Acteón.'
            RESULT: A dynamic, mythological art style painting depicting the scene '5. El Destino de Acteón.' In the foreground, Actaeon is caught mid-transformation, his body shifting into that of a stag, his face frozen in shock and fear. Surrounding him are a pack of fierce hunting dogs, leaping toward him with snarling jaws. The forest behind is dense and shadowy, with beams of light breaking through the trees. The bold text '5. El Destino de Acteón' is formed by twisting branches and vines, curling upward into the sky, contrasting against the muted greens and golds of the forest landscape at twilight.

            TEXT: '6. El Suplicio de Prometeo.'
            RESULT: A powerful, dramatic art style painting portraying '6. El Suplicio de Prometeo.' Prometheus is chained to a jagged mountain peak, his body contorted in agony. Above him, a massive eagle descends with its wings outstretched, ready to feast on his liver. The sky is stormy, with bolts of lightning illuminating the harsh, barren landscape around him. The bold text '6. El Suplicio de Prometeo' is carved into the dark, craggy rocks of the mountain, standing out against the glowing cracks of lava seeping from the ground.

            TEXT: '7. La Maldición de Casandra.'
            RESULT: A melancholic, ethereal art style painting illustrating the scene '7. La Maldición de Casandra.' In the center, Cassandra stands on the steps of a grand palace, her face twisted in despair as she gazes into the distance, her eyes wide with the knowledge of impending doom. Behind her, the people of Troy ignore her warnings, continuing their daily lives, oblivious to the coming destruction. The sky is a muted twilight, with dark clouds slowly rolling in. The bold text '7. La Maldición de Casandra' is formed by delicate wisps of mist rising from the ground, contrasting against the fading golden glow of the city in the background.
            
            Return only the image description, without any additional text or explanation.
            """
        
    class OutputFormats(ValueEnum):
        GENERATE_STORYBOARD_OUTPUT_FORMAT = """
            Return only the array of dictionaries, with no additional text or explanation. The array should be in the format. When describing the image do not use more than 50 words: 
            [
                {"text": "Scene 1 text in original language", "image": "Detailed image description for scene 1 in English"},
                {"text": "Scene 2 text in original language", "image": "Detailed image description for scene 2 in English"},
                ...
            ]
            """

class Styles():
    class Flux(ValueEnum):
        DARK_ATMOSPHERE = """
        When creating the image description, add a horrific style inspired by the following elements:

        - Lovecraftian cosmic horror: vast, unknowable entities, tentacles, non-Euclidean geometry
        - Giger-esque biomechanical nightmares: fusion of flesh and machine, intricate details
        - Beksiński's hellish landscapes: surreal, decaying structures, muted color palettes
        - Junji Ito's body horror: grotesque transformations, spiral motifs, unsettling close-ups
        - Gothic horror ambiance: fog-shrouded castles, gargoyles, candlelit corridors
        - Clive Barker's hellraiser aesthetics: chains, hooks, leather, intricate puzzle boxes
        - Silent Hill's rust and decay: abandoned, corroded environments, ash-like particles
        - Dario Argento's vivid color schemes: stark reds and blues in shadowy scenes
        - Francis Bacon's distorted figures: warped, screaming faces, isolated in void-like spaces
        - Dark surrealism: melting realities, impossible creatures, dreamlike terror

        Atmosphere keywords: oppressive, claustrophobic, uncanny, dread-inducing, nightmarish
        Visual elements: deep shadows, harsh contrasts, unsettling symmetry, eerie lighting
        Textures: visceral, slimy, decaying, chitinous, veiny, pulsating
        Color palettes: muted with vivid accents, deep crimsons, sickly greens, void-like blacks
        """
        MITO_TV = """
    When creating the image description, add a creative style inspired by the following words elements:
    intricate details, ultrafine detail, vibrant color, 8k resolution masterpiece, cinematic raw realism, UHDR,32K, ultra-detailed ,   metallic plating
    """