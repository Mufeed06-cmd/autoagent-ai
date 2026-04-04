from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.intent_router import classify_intent
from core.executor import extract_and_run_code
from skills.file_ops import handle_file_command
from skills.app_launcher import handle_app_command
from skills.web_search import web_search
from skills.memory import (
    remember, recall, recall_all, forget,
    add_history, get_history, load_memory
)
import requests as req

app = Flask(__name__)
CORS(app)  # Allow frontend to talk to this API

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:7b"

# Load memory into system prompt at startup
def build_system_prompt():
    mem = load_memory()
    facts_str = ""
    if mem["facts"]:
        facts_str = "\nKnown facts about user:\n" + "\n".join(
            [f"- {k}: {v}" for k, v in mem["facts"].items()]
        )
    return (
        "You are AutoAgent AI, a powerful coding and system assistant. "
        "Always wrap code in fenced blocks with language tags: "
        "```python, ```c, ```bash etc."
        + facts_str
    )

# In-memory chat history for current session
chat_messages = [
    {"role": "system", "content": build_system_prompt()}
]

def ask_ollama(messages):
    response = req.post(OLLAMA_URL, json={
        "model": MODEL,
        "messages": messages,
        "stream": False
    })
    return response.json()["message"]["content"]

def handle_memory_command(user_input: str) -> str:
    text = user_input.lower().strip()
    if "remember" in text:
        rest = user_input[user_input.lower().find("remember") + 8:].strip()
        if " is " in rest:
            parts = rest.split(" is ", 1)
            key = parts[0].strip().replace("my ", "")
            value = parts[1].strip()
            return remember(key, value)
        return "Say it like: remember my name is Nakeeb"
    if "forget" in text:
        rest = user_input[user_input.lower().find("forget") + 6:].strip()
        return forget(rest)
    if any(w in text for w in ["what do you know", "recall all", "show memory", "my info"]):
        return recall_all()
    if "recall" in text:
        rest = user_input[user_input.lower().find("recall") + 6:].strip()
        return recall(rest)
    return recall_all()

# ─── ROUTES ────────────────────────────────────────────

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "AutoAgent AI is running",
        "version": "1.0.0",
        "endpoints": ["/chat", "/memory", "/history", "/status"]
    })

@app.route("/status", methods=["GET"])
def status():
    try:
        req.get("http://localhost:11434", timeout=2)
        ollama_status = "online"
    except:
        ollama_status = "offline"
    return jsonify({
        "autoagent": "running",
        "ollama": ollama_status,
        "model": MODEL
    })

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_input = data["message"].strip()
    intent = classify_intent(user_input)

    response_text = ""

    if intent == "file":
        response_text = handle_file_command(user_input)

    elif intent == "app":
        response_text = handle_app_command(user_input)

    elif intent == "search":
        response_text = web_search(user_input)

    elif intent == "memory":
        response_text = handle_memory_command(user_input)

    elif intent == "code":
        chat_messages.append({"role": "user", "content": user_input})
        response_text = ask_ollama(chat_messages)
        chat_messages.append({"role": "assistant", "content": response_text})
        add_history("user", user_input)
        add_history("assistant", response_text)

    else:  # chat
        chat_messages.append({"role": "user", "content": user_input})
        response_text = ask_ollama(chat_messages)
        chat_messages.append({"role": "assistant", "content": response_text})
        add_history("user", user_input)
        add_history("assistant", response_text)

    return jsonify({
        "intent": intent,
        "response": response_text
    })

@app.route("/memory", methods=["GET"])
def get_memory():
    mem = load_memory()
    return jsonify(mem["facts"])

@app.route("/memory", methods=["POST"])
def set_memory():
    data = request.json
    if not data or "key" not in data or "value" not in data:
        return jsonify({"error": "Provide key and value"}), 400
    result = remember(data["key"], data["value"])
    return jsonify({"result": result})

@app.route("/memory/<key>", methods=["DELETE"])
def delete_memory(key):
    result = forget(key)
    return jsonify({"result": result})

@app.route("/history", methods=["GET"])
def history():
    return jsonify(get_history())

@app.route("/history", methods=["DELETE"])
def clear_history():
    mem = load_memory()
    mem["history"] = []
    from skills.memory import save_memory
    save_memory(mem)
    return jsonify({"result": "History cleared"})

if __name__ == "__main__":
    print("=" * 50)
    print("  AutoAgent API — Running on http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)