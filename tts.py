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
        tts = gTTS(text, lang=voice.value['lang'], tld=voice.value['tld'])
        tts.save(output_file)
        return output_file

class EdgeTTS(TTS):
    @staticmethod
    def generate_speech(
        text: str,
        output_file: Path,
        model: TTSModels,
        voice: Voices.Azure = Voices.Azure.BOLIVIA
    ) -> Path:
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

        speech_file_path = Path(output_file)
        response = client.audio.speech.create(
            model=model.value,
            voice=voice.value,
            input=text
        )

        response.stream_to_file(speech_file_path)
        return str(speech_file_path)
    

if __name__ == "__main__":
    OpenaiTTS.generate_speech(
        text="hola mundo",
        output_file=Path("hola_mundo.mp3")
    )