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
    
    class ElevenLabs(Enum):
        RACHEL = "Rachel"
        DOMI = "Domi"
        BELLA = "Bella"
        HERNAN_CORTES = "W5JElH3dK1UYYAiHH7uh"
        SARA_MARTIN_2 = "Ir1QNHvhaJXbAGhT50w3"
        Martin_Osborne_6 = "LlZr3QuzbW4WrPjgATHG"
        DAN_DAN = "9F4C8ztpNUmXkdDDbz3J"

class TTSModels(Enum):
    GOOGLE = 'google'
    AZURE = 'azure'
    OPENAI_TTS_1 = 'tts-1'
    OPENAI_TTS_1_HD = 'tts-1-hd'
    ELEVENLABS_MULTILINGUAL_V2 = "eleven_multilingual_v2"


class ImageGenerators(Enum):
    FAKE = 'FAKE'
    SDXL_TURBO = 'stabilityai/sdxl-turbo'
    SD3 = 'stabilityai/stable-diffusion-3-medium-diffusers'
    FLUX1_SCHNELL = 'black-forest-labs/FLUX.1-schnell'

class ImageGeneratorConfig(Enum):
    FLUX1_SCHNELL = {
        'height': 1280,
        'width': 768,
        'num_inference_steps': 1,
        'guidance_scale': 0.0
    }
    SDXL_TURBO = {
        'num_inference_steps': 5,
        'guidance_scale': 0.0
    }

class LLMModels(Enum):
    GPT4o = 'gpt-4o'
    GPT4oMini ='gpt-4o-mini'
    LLAMA31_8B = 'meta-llama/Meta-Llama-3.1-8B-Instruct'
    O1Mini = 'o1-mini'
    O1Preview = 'o1-preview'
    CLAUDE_3_5_sonnet = 'claude-3-5-sonnet-20240620'

class LLMCosts(Enum):
    #https://www.anthropic.com/pricing#anthropic-api
    CLAUDE_3_5_sonnet = {
        'input': 3/10**6,  # $3 / MTok
        'output': 15/10**6  # $15 / MTok
    }

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