import time
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from langchain_core.messages import HumanMessage
from config import LOGS_FILE, IMAGES_DIR, AUDIOVIDEO_DIR
from helpers import log_event, log_user_message, build_conversation, img_to_base64
from llm import choose_llm, run_llm_async
from transcribe import run_transcriber_async


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Project by TIDO, for SEA Developer Challenge.\n"
        "Send a text or an image (optionally with a caption) to test our AI bot!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    username = msg.from_user.username or str(msg.from_user.id)
    ts = int(time.time())

    log_event(LOGS_FILE, type="raw_message", data=msg.to_dict())

    conversation = build_conversation(username)

    # If user sends IMAGE:
    if msg.photo:
        photo = msg.photo[-1]
        photo_file = await photo.get_file()
        photo_path = IMAGES_DIR / f"{username}_{ts}.jpg"
        await photo_file.download_to_drive(photo_path)

        caption = (msg.caption or "").strip()
        human_parts = []
        if caption:
            human_parts.append({"type": "text", "text": caption})
        human_parts.append(img_to_base64(photo_path))

        conversation.append(HumanMessage(content=human_parts))

        llm = choose_llm(use_vision=True)
        try:
            response = await run_llm_async(llm, conversation)
        except Exception as e:
            await msg.reply_text("⚠️ Error processing image.")
            log_event(LOGS_FILE, type="error", error=str(e))
            return

        ai_text = response.content
        log_user_message(username, username, f"[Image: {photo_path.name}] Caption: {caption}")
        log_user_message(username, "GovReport", ai_text)
        await msg.reply_text(ai_text)
        return

    # If user sends AUDIO / VIDEO:
    if msg.audio or msg.voice or msg.video or msg.video_note:
        audio_file = msg.audio or msg.voice or msg.video or msg.video_note
        file_obj = await audio_file.get_file()
        audio_path = AUDIOVIDEO_DIR / f"{username}_{ts}.ogg"
        await file_obj.download_to_drive(audio_path)

        transcription = await run_transcriber_async(str(audio_path))
        text = (transcription or "").lstrip().capitalize()
        conversation.append(HumanMessage(content=text))

        llm = choose_llm(use_vision=False)
        try:
            response = await run_llm_async(llm, conversation)
        except Exception as e:
            await msg.reply_text("⚠️ Error processing audio/video.")
            log_event(LOGS_FILE, type="error", error=str(e))
            return

        ai_text = response.content
        log_user_message(username, username, f"[Audio/Video: {audio_path.name}]")
        log_user_message(username, "GovReport", ai_text)
        await msg.reply_text(ai_text)
        return

    # If user sends TEXT:
    text = (msg.text or "").strip()
    conversation.append(HumanMessage(content=text))

    llm = choose_llm(use_vision=False)
    try:
        response = await run_llm_async(llm, conversation)
    except Exception as e:
        await msg.reply_text("⚠️ Error processing text.")
        log_event(LOGS_FILE, type="error", error=str(e))
        return

    ai_text = response.content
    log_user_message(username, username, text)
    log_user_message(username, "GovReport", ai_text)
    await msg.reply_text(ai_text)