import requests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.intent_router import classify_intent
from core.executor import extract_and_run_code
from skills.file_ops import handle_file_command
from skills.app_launcher import handle_app_command
from skills.web_search import web_search
from skills.voice_input import listen_once
from skills.memory import (
    remember, recall, recall_all, forget,
    add_history, get_history, load_memory
)

def ask_ollama(messages):
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "qwen2.5-coder:7b",
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

# Load memory into system prompt
mem = load_memory()
facts_str = ""
if mem["facts"]:
    facts_str = "\nKnown facts about user:\n" + "\n".join(
        [f"- {k}: {v}" for k, v in mem["facts"].items()]
    )

messages = [
    {"role": "system", "content": (
        "You are AutoAgent AI, a powerful coding and system assistant. "
        "Always wrap code in fenced blocks with language tags: ```python, ```c, ```bash etc."
        + facts_str
    )}
]

# Voice mode toggle
voice_mode = False

print("=" * 50)
print("  AutoAgent AI — Ready")
print("  Type 'exit' to quit")
print("  Type 'voice on' to enable voice input")
print("  Type 'voice off' to disable voice input")
print("=" * 50)

while True:
    # Get input — voice or text
    if voice_mode:
        print("\n[Voice Mode ON] Press Enter to speak, or type a command:")
        trigger = input()
        if trigger.strip():
            user_input = trigger.strip()
        else:
            user_input = listen_once()
            if not user_input:
                continue
    else:
        user_input = input("\n> ").strip()

    if not user_input:
        continue

    # Voice mode toggle commands
    if user_input.lower() == "voice on":
        voice_mode = True
        print("[AutoAgent]: Voice mode enabled. Press Enter to speak.")
        continue
    if user_input.lower() == "voice off":
        voice_mode = False
        print("[AutoAgent]: Voice mode disabled.")
        continue

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye.")
        break

    intent = classify_intent(user_input)
    print(f"[Intent: {intent}]")

    if intent == "file":
        result = handle_file_command(user_input)
        print(f"[AutoAgent]: {result}")

    elif intent == "app":
        result = handle_app_command(user_input)
        print(f"[AutoAgent]: {result}")

    elif intent == "search":
        print(f"[AutoAgent]: Searching...")
        result = web_search(user_input)
        print(f"[AutoAgent]:\n{result}")

    elif intent == "memory":
        result = handle_memory_command(user_input)
        print(f"[AutoAgent]: {result}")

    elif intent == "code":
        messages.append({"role": "user", "content": user_input})
        response = ask_ollama(messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n[AutoAgent]: {response}")
        extract_and_run_code(response)
        add_history("user", user_input)
        add_history("assistant", response)

    else:
        messages.append({"role": "user", "content": user_input})
        response = ask_ollama(messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n[AutoAgent]: {response}")
        add_history("user", user_input)
        add_history("assistant", response)