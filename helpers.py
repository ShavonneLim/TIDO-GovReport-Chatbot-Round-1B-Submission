import json
import base64
import mimetypes
import time
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from config import SYSTEM_PROMPT, MESSAGES_DIR

def log_event(file_path: Path, **kwargs):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    kwargs["logged_at"] = int(time.time())
    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(kwargs, ensure_ascii=False) + "\n")

def read_user_messages(username: str) -> list[dict]:
    user_file = MESSAGES_DIR / f"{username}_messages.jsonl"
    if not user_file.exists():
        return []
    with user_file.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def log_user_message(username: str, sender: str, text: str):
    log_event(MESSAGES_DIR / f"{username}_messages.jsonl", sender=sender, text=text)

def img_to_base64(path: Path) -> dict:
    mime = mimetypes.guess_type(str(path))[0] or "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode("utf-8")
    return {"type": "image", "source_type": "base64", "mime_type": mime, "data": data}

def build_conversation(username: str) -> list:
    prev = read_user_messages(username)
    msgs = [SystemMessage(content=SYSTEM_PROMPT)]
    for entry in prev:
        if entry["sender"].lower() in {"GovReport", "assistant"}:
            msgs.append(AIMessage(content=entry["text"]))
        else:
            msgs.append(HumanMessage(content=entry["text"]))
    return msgs