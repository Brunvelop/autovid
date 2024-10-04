import textwrap
from enum import Enum

class ValueEnum(Enum):
    def __get__(self, obj, objtype):
        value = self.value
        if isinstance(value, str):
            value = textwrap.dedent(value).strip()
            return value[1:] if value.startswith('\n') else value
        return value

class WriterPrompts:
    class System(ValueEnum):
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
            Responde únicamente con True si el texto es históricamente preciso, o False si contiene inexactitudes históricas.
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