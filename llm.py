import asyncio
from langchain_ollama import ChatOllama
from config import OLLAMA_MODEL_TEXT, OLLAMA_MODEL_VISION

def choose_llm(use_vision: bool) -> ChatOllama:
    model = OLLAMA_MODEL_VISION if use_vision else OLLAMA_MODEL_TEXT
    return ChatOllama(model=model)

async def run_llm_async(llm, conversation):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: llm.invoke(conversation))