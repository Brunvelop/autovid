import textwrap
from enum import Enum

class ValueEnum(Enum):
    def __get__(self, obj, objtype):
        value = self.value
        if isinstance(value, str):
            value = textwrap.dedent(value).strip()
            return value[1:] if value.startswith('\n') else value
        return value

class WriterPrompts():
    class System(ValueEnum):
        THEME_WRITER = """
            Eres un guionista experto en {expertise}, capaz de crear guiones irresistibles que capturan la atención
            de lectores de todas las edades. Narras con claridad y encanto, explicando cualquier concepto que pueda
            generar dudas y manteniendo al público enganchado hasta el final.
        """
    
    class User(ValueEnum):
        SHORTS_TEXT_GENERATOR = """
            Antes de comenzar, aquí están los detalles importantes:

            Tema del vídeo:
            <tema>
            {theme}
            </tema>

            Número de palabras objetivo:
            <numero_palabras>
            {words_number}
            </numero_palabras>

            Instrucciones:

            1. Genera un hook breve y directo, de una sola frase, que capte la atención inmediata. 
            Usa estrategias como disonancia cognitiva, curiosidad, vulnerabilidad, paradoja o urgencia
            para provocar una pausa y crear un fuerte deseo de seguir leyendo. 
            Cada palabra debe ser impactante y precisa.

            2. Estructura tu guion siguiendo estos elementos narrativos:
            - Introducción: Presenta el tema y la idea principal
            - Desarrollo: Desarrolla el tema con puntos de apoyo
            - Clímax: Destaca el aspecto más importante o interesante
            - Resolución: Resume los puntos clave o llama a la acción

            3. Apunta a escribir aproximadamente el número de palabras especificado en <numero_palabras>.

            4. Utiliza un lenguaje claro y conciso, manteniendo un tono conversacional adecuado para un artículo 
            para iniciados en el tema. No omitas información que pueda desconocer el lector. Contextualiza todo
            lo necesario para que sea un articulo pleno y autoconclusivo.

            5. Incluye recursos retóricos como metáforas, analogías, símiles, hipérboles, anáforas y aliteraciones 
            para potenciar el compromiso del espectador. Utiliza imágenes vívidas, contrastes impactantes 
            y juegos de palabras que despierten emociones, generen curiosidad y hagan que el mensaje resuene
            de manera memorable y duradera en el espectador.

            6. Asegúrate de que todo el contenido de tu guion se relacione y apoye el tema proporcionado en <tema>.

            Antes de escribir el guion final, desarrolla tus ideas dentro de las etiquetas <planning>. En esta sección:
            - Desglosa el tema en puntos clave o aspectos a cubrir.
            - Contexto e informacion para aclarar a un lector que desconozca el tema.
            - Haz una lluvia de ideas de posibles "ganchos" para la introducción.
            - Esboza la estructura del guion.
            - Anota posibles recursos retóricos que podrías utilizar.

            Luego, presenta el guion final dentro de las etiquetas <text>, escribiendo el texto de forma continua 
            sin etiquetas de sección.

            Recuerda:
            - Verifica que tu guion se adhiera al tema dado
            - Asegúrate de que el recuento de palabras sea cercano al objetivo
            - Revisa tu guion para garantizar coherencia, atractivo y fluidez
            - Garantiza la veracidad historica del texto

            Comienza ahora con tu proceso de planificación y la creación del guion.
        """
        SHORTS_TEXT_IMPROVER = """
            Eres un experto en mejorar y clarificar textos, haciéndolos más accesibles y atractivos para
            nuevos lectores sobre el tema. Tu tarea es analizar y mejorar el siguiente texto,
            ajustando la longitud a aproximadamente {words_number} palabras:

            <texto_original>
            {text}
            </texto_original>

            Por favor, sigue estos pasos para mejorar el texto:

            1. Analiza cuidadosamente el texto original. En las etiquetas <análisis>, proporciona:
            - Identificación del tema principal y propósito del texto original.
            - Lista de términos clave o conceptos que puedan necesitar explicación.
            - Puntos que puedan ser poco claros o desconocidos para un nuevo lector.
            - Consideraciones sobre cómo mejorar el tono general para hacerlo más accesible y entretenido.
            - Ideas de ejemplos o analogías atractivas que podrían usarse.
            - Lista de imprecisiones historicas o elementos que no pertenecen a la historia original

            2. Planea los cambios a ejecutar en el texto para hacerlo mas claro y accesible en la etiqueta <plan>:
            - Propuestas para explicar estos puntos de manera más simple o proporcionar contexto adicional.
            - Plan para aumentar la participación del lector mediante técnicas de escritura atractivas.
            - Correciones de las imprecisiones historicas

            3. Reescribe el texto, incorporando tus mejoras y clarificaciones. En <texto_mejorado>, Asegúrate de:
            - Usar un lenguaje más conversacional.
            - Añadir ejemplos o analogías relevantes.
            - Desglosar ideas complejas en conceptos más simples.
            - Usar la voz activa con más frecuencia.
            - Incorporar preguntas retóricas para involucrar al lector.
            - Crear una introducción atractiva.
            - Corrige las imprecisiones historicas si las hay
            - Usar párrafos y oraciones más cortas para mejorar la legibilidad.
            - Añadir subtítulos si es apropiado para dividir el texto.
            - Concluir con una declaración que invite a la reflexión o a la acción.
            - Mantener la longitud del texto en aproximadamente {words_number} palabras.

            Recuerda, tu objetivo es hacer que el texto sea más claro y atractivo mientras mantienes su mensaje
            e intención original, todo en español y con la longitud especificada.

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
    GENERATE_STORYBOARD_OUTPUT_FORMAT = """
        Return only the array of dictionaries, with no additional text or explanation. The array should be in the format. When describing the image do not use more than 50 words: 
        [
            {"text": "Scene 1 text in original language", "image": "Detailed image description for scene 1 in English"},
            {"text": "Scene 2 text in original language", "image": "Detailed image description for scene 2 in English"},
            ...
        ]
        """

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

class Styles():
    class Flux(ValueEnum):
        MITO_TV = """
            When creating the image description, add a creative style inspired by the following words elements:
            intricate details, ultrafine detail, vibrant color, 8k resolution masterpiece, cinematic raw realism, UHDR,32K, ultra-detailed, metallic plating
        """

class AgentPrompts(ValueEnum):
    SHORTS_WRITER = """
    
    """