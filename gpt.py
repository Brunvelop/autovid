
import os

from tqdm import tqdm
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser

import prompts
import samples

class ListOfDictsOutputParser:
    def parse(self, output):
        # Aquí asumimos que la salida es una cadena que representa una lista de diccionarios en formato JSON.
        # Usamos json.loads para convertir la cadena en una lista de diccionarios.
        import json
        return json.loads(output)

def generate_video_script_json(content):
    load_dotenv()

    chat_model = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name='gpt-4' # type: ignore
    )

    template = ChatPromptTemplate.from_messages([
        # ("system", "Eres un progrma experto en generar videos virales para tiktok. {output_format}"),
        # ("human", "Escribe el guión y las imagenes para un video viral sobre {content}. {output_format}"),
        ("system", "You are an expert program in generating viral videos for TikTok.. {output_format}"),
        ("human", "Write the script and the images for a viral video about {content}. {output_format}"),
    ])

    output_format = '''Escribe el contenido en forma de un array de diccionarios de python donde el primer elemento sea el texto a leer y el segundo la descripcion de la imagen. Debe tener esta forma [{"text":"", "image":""},{...},...]'''
    output_format ='''Write the content in the form of an array of Python dictionaries where the first element is the text to read and the second is the description of the image. It should have this form: [{"text":"", "image":""},{...},...]'''
    messages = template.format_messages(
        output_format=output_format,
        content=content
    )

    output_parser = ListOfDictsOutputParser()

    output = chat_model(messages)
    output_parsed = output_parser.parse(output.content)
    return output_parsed

def generate_video_script(content):
    load_dotenv()

    chat_model = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=1,
        model_name='gpt-4' # type: ignore
    )

    template = ChatPromptTemplate.from_messages([
        ("system", prompts.generate_video_script_system_prompt + samples.generate_video_script_samples),
        ("human", "Escribe el script para un video sobre {content}. {output_format}"),
    ])

    output_format = '''no uses mas de 100 palabras, No utilices saltos de linea ni \n '''
    messages = template.format_messages(
        output_format=output_format,
        content=content
    )

    output = chat_model(messages)

    return output.content

def generate_images_description_and_split_text(script):
    load_dotenv()

    chat_model = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=1,
        model_name='gpt-4'
    )

    template = ChatPromptTemplate.from_messages([
        ("system", prompts.generate_images_description_and_split_text_system + samples.generate_images_description_and_split_text),
        ("human", "Transform this text: {script}. {output_format}.  Return only an array [] do not whirte any thing else."),
    ])

    output_format = prompts.generate_images_description_and_split_text_output_format
    messages = template.format_messages(
        script=script,
        output_format=output_format
    )


    output_parser = ListOfDictsOutputParser()

    output = chat_model(messages)
    output_parsed = output_parser.parse(output.content)
    return output_parsed


def sort_scripts(array_scripts):
    load_dotenv()

    chat_model = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        temperature=1,
        model_name='gpt-4' # type: ignore
    )

    template = ChatPromptTemplate.from_messages([
        ("system", "{output_format}"),
        ("human", "Ordena de mayor potencial viral a menor estos textos para videos {content}. {output_format}"),
    ])

    output_format = '''Recuerda devolver un array de la forma [2,1,4,0,3,...]'''
    messages = template.format_messages(
        output_format=output_format,
        content=array_scripts
    )

    output = chat_model(messages)

    return output.content