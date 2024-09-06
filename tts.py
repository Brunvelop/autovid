import os
import asyncio
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
    

if __name__ == "__main__":
    import json

    SHORT_N = 2
    SHORTS_FOLDER = Path('data/HOMERO/LA_ILIADA/CAPITULO_001/SHORTS')
    with open(SHORTS_FOLDER / f'{SHORT_N}/text/storyboard.json', 'r', encoding='utf-8') as f:
        storyboard = json.load(f)

    for i, scene in enumerate(storyboard):
        print(EdgeTTS.generate_speech(
            text=scene.get('text'),
            output_file= SHORTS_FOLDER / f'{SHORT_N}/audios/{i}.mp3',
        ))