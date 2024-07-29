import os
import asyncio
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

import edge_tts
from gtts import gTTS
from openai import OpenAI

from definitions import Voices, TTSModels

class TTS:
    @staticmethod
    def _generate_gtts(
            text: str,
            output_file: Path,
            voice: Voices.Google = Voices.Google.SPAIN
        ) -> Path:
        tts = gTTS(text, lang=voice.value['lang'], tld=voice.value['tld'])
        tts.save(output_file)
        return output_file

    @staticmethod
    def _generate_edgetts(
            text: str,
            output_file: Path,
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

    @staticmethod
    def _generate_openai_tts(
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
    
    @classmethod
    def generate_tts(
            cls,
            text: str, 
            output_file: Path,
            model: TTSModels,
            voice: Optional[Voices] = None,
        ) -> Path:
        if model == TTSModels.GOOGLE:
            voice = voice or Voices.Google.SPAIN
            return cls._generate_gtts(text, output_file, voice)
        elif model == TTSModels.AZURE:
            voice = voice or Voices.Azure.BOLIVIA
            return cls._generate_edgetts(text, output_file, voice)
        elif model == TTSModels.OPENAI_TTS_1 or TTSModels.OPENAI_TTS_1_HD:
            voice = voice or Voices.OpenAI.ALLOY
            return cls._generate_openai_tts(text, output_file, voice, model)
        else:
            raise ValueError(f"Modelo TTS no soportado: {model}")
    

if __name__ == "__main__":
    TTS.generate_tts(
        text="hola mundo",
        output_file=Path("hola_mundo.mp3"),
        model=TTSModels.GOOGLE,
        voice=Voices.Google.MEXICO
    )