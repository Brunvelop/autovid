from enum import Enum, auto
from typing import List, Dict, TypedDict

class Voices:
    class Google(Enum):
        MEXICO = {'lang': 'es', 'tld': 'com.mx'}
        SPAIN = {'lang': 'es', 'tld': 'es'}
        USA = {'lang': 'es', 'tld': 'us'}

    class Azure(Enum):
        ARGENTINA = 'es-AR-ElenaNeural'
        BOLIVIA = 'es-BO-MarceloNeural'
        CHILE = 'es-CL-LorenzoNeural'
        COSTA_RICA = 'es-CR-JuanNeural'
        DOMINICAN_REPUBLIC = 'es-DO-RamonaNeural'
        GUATEMALA = 'es-GT-AndresNeural'
        HONDURAS = 'es-HN-KarlaNeural'
        PANAMA = 'es-PA-RobertoNeural'
        PUERTO_RICO = 'es-PR-KarinaNeural'

    class OpenAI(Enum):
        ALLOY = 'alloy'
        ECHO = 'echo'
        FABLE = 'fable'
        ONYX = 'onyx'
        NOVA = 'nova'
        SHIMMER = 'shimmer'

class TTSModels(Enum):
    GOOGLE = 'google'
    AZURE = 'azure'
    OPENAI_TTS_1 = 'tts-1'
    OPENAI_TTS_1_HD = 'tts-1-hd'

class SDModels(Enum):
    FAKE = 'FAKE'
    SDXL_TURBO = 'stabilityai/sdxl-turbo'
    SD3 = 'stabilityai/stable-diffusion-3-medium-diffusers'
    FLUX1_SCHNELL = 'black-forest-labs/FLUX.1-schnell'

class LLMModels(Enum):
    GPT4o = 'gpt-4o'
    GPT4oMini ='gpt-4o-mini'
    LLAMA31_8B = 'meta-llama/Meta-Llama-3.1-8B-Instruct'

class VideatorTasks(Enum):
    WRITE = auto()
    AUDIO = auto()
    IMAGES = auto()
    VIDEO = auto()
    FULL = auto()

class SceneFull(TypedDict):
    numero_escena: int
    descripcion_imagen: str
    dialogo: str
    acciones: str
    movimientos_camara: str
    sonidos: str
    duracion: str

class Scene(TypedDict):
    text: str
    image: str

Storyboard = List[Scene]