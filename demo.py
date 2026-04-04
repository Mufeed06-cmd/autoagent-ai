import requests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.intent_router import classify_intent
from core.executor import extract_and_run_code
from skills.file_ops import handle_file_command
from skills.app_launcher import handle_app_command

def ask_ollama(messages):
    response = requests.post("http://localhost:11434/api/chat", json={
        "model": "qwen2.5-coder:7b",
        "messages": messages,
        "stream": False
    })
    return response.json()["message"]["content"]

messages = [
    {"role": "system", "content": (
        "You are AutoAgent AI, a powerful coding and system assistant. "
        "Always wrap code in fenced blocks with language tags: ```python, ```c, ```bash etc."
    )}
]

print("=" * 50)
print("  AutoAgent AI — Ready")
print("  Type 'exit' to quit")
print("=" * 50)

while True:
    user_input = input("\n> ").strip()
    if not user_input:
        continue
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye.")
        break

    # Classify intent
    intent = classify_intent(user_input)
    print(f"[Intent: {intent}]")

    if intent == "file":
        result = handle_file_command(user_input)
        print(f"[AutoAgent]: {result}")

    elif intent == "app":
        result = handle_app_command(user_input)
        print(f"[AutoAgent]: {result}")

    elif intent == "code":
        messages.append({"role": "user", "content": user_input})
        response = ask_ollama(messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n[AutoAgent]: {response}")
        extract_and_run_code(response)

    else:  # chat
        messages.append({"role": "user", "content": user_input})
        response = ask_ollama(messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n[AutoAgent]: {response}")