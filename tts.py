import os
import asyncio
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from abc import ABC, abstractmethod

import edge_tts
from gtts import gTTS
from openai import OpenAI

from definitions import Voices, TTSModels

class TTS(ABC):
    @staticmethod
    @abstractmethod
    def generate_speech(
        text: str, 
        output_file: Path,
        model: TTSModels,
        voice: Optional[Voices] = None,
    ) -> Path:
        pass

class GoogleTTS(TTS):
    @staticmethod
    def generate_speech(
        text: str,
        output_file: Path,
        model: TTSModels,
        voice: Voices.Google = Voices.Google.SPAIN
    ) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        tts = gTTS(text, lang=voice.value['lang'], tld=voice.value['tld'])
        tts.save(output_file)
        return output_file

class EdgeTTS(TTS):
    @staticmethod
    def generate_speech(
        text: str,
        output_file: Path,
        model: TTSModels = None,
        voice: Voices.Azure = Voices.Azure.BOLIVIA
    ) -> Path:
        output_file.parent.mkdir(parents=True, exist_ok=True)

        async def amain() -> None:
            communicate = edge_tts.Communicate(text, voice.value)
            await communicate.save(output_file)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(amain())
        finally:
            loop.close()

        return output_file

class OpenaiTTS(TTS):
    @staticmethod
    def generate_speech(
        text: str, 
        output_file: Path,
        voice: Voices.OpenAI = Voices.OpenAI.ALLOY,
        model: TTSModels = TTSModels.OPENAI_TTS_1
    ) -> Path:
        load_dotenv()
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        output_file.parent.mkdir(parents=True, exist_ok=True)
        speech_file_path = Path(output_file)
        response = client.audio.speech.create(
            model=model.value,
            voice=voice.value,
            input=text
        )

        response.stream_to_file(speech_file_path)
        return str(speech_file_path)
    
class ElevenLabsTTS(TTS):
    @staticmethod
    def generate_speech(
        text: str,
        output_file: Path,
        model: TTSModels = TTSModels.ELEVENLABS_MULTILINGUAL_V2,
        voice: Voices.ElevenLabs = Voices.ElevenLabs.HERNAN_CORTES
    ) -> Path:
        load_dotenv()
        XI_API_KEY = os.getenv("ELEVENLABS_API_KEY")

        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice.value}/stream"
        
        headers = {
            "Accept": "application/json",
            "xi-api-key": XI_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": model.value,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8
            }
        }
        
        response = requests.post(url, json=data, headers=headers, stream=True)
        
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return output_file
        else:
            raise Exception(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    import json

    N = 14
    STORYBOARD = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/text/storyboard.json')

    with open(STORYBOARD, 'r', encoding='utf-8') as f:
        storyboard = json.load(f)

    for i, scene in enumerate(storyboard):
        print(ElevenLabsTTS.generate_speech(
            text=scene.get('text'),
            output_file=Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/audios/{i}.mp3'),
            voice=Voices.ElevenLabs.DAN_DAN
        ))

    