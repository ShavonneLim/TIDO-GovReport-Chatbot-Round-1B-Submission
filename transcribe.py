import whisper
import asyncio
from config import WHISPER_MODEL_AUDIO, WHISPER_CHOSENLANGUAGE

def sync_transcribe(audio_path: str):
    chosenLanguage = WHISPER_CHOSENLANGUAGE
    transcriberModel = whisper.load_model(WHISPER_MODEL_AUDIO)

    # Transcribe the audio using Whisper AI & Clean up transcription
    return transcriberModel.transcribe(audio_path, language=chosenLanguage)["text"]

async def run_transcriber_async(audio_path: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_transcribe, audio_path)