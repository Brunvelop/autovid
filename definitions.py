from enum import Enum, auto

class GTTSVoices(Enum):
    MEXICO = {'lang': 'es', 'tld': 'com.mx'}
    SPAIN = {'lang': 'es', 'tld': 'es'}
    USA = {'lang': 'es', 'tld': 'us'}

class AzureVoices(Enum):
    ARGENTINA = 'es-AR-ElenaNeural'
    BOLIVIA = 'es-BO-MarceloNeural'
    CHILE = 'es-CL-LorenzoNeural'
    COSTA_RICA = 'es-CR-JuanNeural'
    DOMINICAN_REPUBLIC = 'es-DO-RamonaNeural'
    GUATEMALA = 'es-GT-AndresNeural'
    HONDURAS = 'es-HN-KarlaNeural'
    PANAMA = 'es-PA-RobertoNeural'
    PUERTO_RICO = 'es-PR-KarinaNeural'

class OpenAIVoices(Enum):
    ALLOY = 'alloy'
    ECHO = 'echo'
    FABLE = 'fable'
    ONYX = 'onyx'
    NOVA = 'nova'
    SHIMMER = 'shimmer'

class OpenAITTSModels(Enum):
    TTS_1 = 'tts-1'
    TTS_1_HD = 'tts-1-hd'

class TTSModels(Enum):
    GOOGLE = auto()
    AZURE = auto()
    OPENAI = auto()

class SDModels(Enum):
    FAKE = "FAKE"
    SDXL_TURBO = "stabilityai/sdxl-turbo"
    # SDXL_BASE = "stabilityai/stable-diffusion-xl-base-1.0"
    # SD_2_1 = "stabilityai/stable-diffusion-2-1"
    # SD_1_5 = "runwayml/stable-diffusion-v1-5"
    # DREAMSHAPER_8 = "Lykon/dreamshaper-8"
    # REALISTIC_VISION_5_1 = "SG161222/Realistic_Vision_V5.1_noVAE"

class VideatorTasks(Enum):
    SCRIPT = auto()
    AUDIO = auto()
    IMAGES = auto()
    VIDEO = auto()
    FULL = auto()