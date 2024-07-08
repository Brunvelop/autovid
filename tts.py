import os
import asyncio
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import edge_tts
from gtts import gTTS
from openai import OpenAI
import definitions

class TTS:
    @staticmethod
    def generate_gtts(text: str, output_file: str,
                       voice: definitions.GTTSVoices = definitions.GTTSVoices.SPAIN) -> str:
        tts = gTTS(text, lang=voice.value['lang'], tld=voice.value['tld'])
        tts.save(output_file)
        return output_file

    @staticmethod
    def generate_edgetts(text: str, output_file: str,
                        voice: definitions.AzureVoices = definitions.AzureVoices.BOLIVIA) -> str:
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
    def generate_openai_tts(text: str, output_file: str,
                            voice: definitions.OpenAIVoices = definitions.OpenAIVoices.ALLOY,
                            model: definitions.OpenAITTSModels = definitions.OpenAITTSModels.TTS_1) -> str:
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

    @staticmethod
    def generate_tts(
        text: str, output_file: str,
        model: definitions.TTSModels,
        voice: Optional[definitions.GTTSVoices or definitions.AzureVoices or definitions.OpenAIVoices] = None,
        tts_model: Optional[definitions.OpenAITTSModels] = None
    ) -> str:
        if model == definitions.TTSModels.GOOGLE:
            voice = voice or definitions.GTTSVoices.SPAIN
            return TTS.generate_gtts(text, output_file, voice)
        elif model == definitions.TTSModels.AZURE:
            voice = voice or definitions.AzureVoices.BOLIVIA
            return TTS.generate_edgetts(text, output_file, voice)
        elif model == definitions.TTSModels.OPENAI:
            voice = voice or definitions.OpenAIVoices.ALLOY
            tts_model = tts_model or definitions.OpenAITTSModels.TTS_1
            return TTS.generate_openai_tts(text, output_file, voice, tts_model)
        else:
            raise ValueError(f"Modelo TTS no soportado: {model}")