import threading
import asyncio
import time
import os
import uuid

from flask import Flask, render_template, jsonify, request, send_from_directory
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# === TELEGRAM CONFIG ===
from config import TELE_API_TOKEN, SYSTEM_PROMPT, IMAGES_DIR
from handlers import start, handle_message
from llm import choose_llm, run_llm_async

# Conversion to integrate with telegram bot messages database schema
def convert_to_messages(messages):
    llm_messages = []
    for m in messages:
        if m['sender'] == 'user':
            llm_messages.append(HumanMessage(content=m['content']))
        elif m['sender'] == 'bot':
            llm_messages.append(AIMessage(content=m['content']))
        # you can ignore images or handle them separately
    return llm_messages

# Conversion to integrate with existing LLM models and prompt templates
def build_conversation(conversation) -> list:
    msgs = [SystemMessage(content=SYSTEM_PROMPT)]
    for entry in conversation:
        if entry["sender"].lower() in {"GovReport", "assistant"}:
            msgs.append(AIMessage(content=entry["text"]))
        else:
            msgs.append(HumanMessage(content=entry["text"]))
    return msgs

# === FLASK SETUP ===
app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = IMAGES_DIR

messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/uploads/<path:filename>')
def serve_uploaded_image(filename):
    return send_from_directory(app.config['UPLOADS_FOLDER'], filename)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/api/upload', methods=['POST'])
async def upload_file():
    global messages
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = "web_" + str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOADS_FOLDER'], filename)
        file.save(filepath)

        image_message = {
            'sender': 'user',
            'type': 'image',
            'content': f'/uploads/{filename}',
            'timestamp': int(time.time() * 1000)
        }
        messages.append(image_message)

        llm = choose_llm(use_vision=True)
        try:
            conversation = convert_to_messages(messages)
            # conversation = build_conversation(conversation)
            response = await run_llm_async(llm, conversation)
        except Exception as e:
            print("⚠️ Error processing image.")
            print(jsonify({'error': str(e)}))
            return jsonify({'error': str(e)}), 500

        bot_content = response.content

        bot_message = {
            'sender': 'bot',
            'type': 'text',
            'content': bot_content,
            'timestamp': int(time.time() * 1000)
        }
        messages.append(bot_message)

        return jsonify({'status': 'success', 'filename': filename}), 200

@app.route('/api/messages', methods=['POST'])
async def send_message():
    global messages
    user_message_data = request.get_json()
    user_content = user_message_data.get('content')

    if not user_content:
        return jsonify({'error': 'Message content is required'}), 400

    user_message = {
        'sender': 'user',
        'type': 'text',
        'content': user_content,
        'timestamp': int(time.time() * 1000)
    }
    messages.append(user_message)

    llm = choose_llm(use_vision=False)
    try:
        conversation = convert_to_messages(messages)
        # conversation = build_conversation(conversation)
        response = await run_llm_async(llm, conversation)
    except Exception as e:
        print("⚠️ Error processing text.")
        print(jsonify({'error': str(e)}))
        return jsonify({'error': str(e)}), 500

    bot_content = response.content

    bot_message = {
        'sender': 'bot',
        'type': 'text',
        'content': bot_content,
        'timestamp': int(time.time() * 1000)
    }
    messages.append(bot_message)

    return jsonify({'status': 'success'})

# === TELEGRAM BOT THREAD ===
def run_telegram():
    asyncio.set_event_loop(asyncio.new_event_loop())  # Create event loop for this thread
    tele_app = ApplicationBuilder().token(TELE_API_TOKEN).build()
    tele_app.add_handler(CommandHandler("start", start))
    tele_app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    print("Telegram bot running…")
    tele_app.run_polling()

# === FLASK THREAD ===
def run_flask():
    print("Flask app running…")
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_telegram, daemon=True).start()
    run_flask()