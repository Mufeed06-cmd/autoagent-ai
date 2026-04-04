import requests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.intent_router import classify_intent
from core.executor import extract_and_run_code
from skills.file_ops import handle_file_command
from skills.app_launcher import handle_app_command
from skills.web_search import web_search
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

    # REMEMBER
    if "remember" in text:
        # Extract key=value style
        # e.g. "remember my name is Nakeeb"
        rest = user_input[user_input.lower().find("remember") + 8:].strip()
        if " is " in rest:
            parts = rest.split(" is ", 1)
            key = parts[0].strip().replace("my ", "")
            value = parts[1].strip()
            return remember(key, value)
        return "Say it like: remember my name is Nakeeb"

    # FORGET
    if "forget" in text:
        rest = user_input[user_input.lower().find("forget") + 6:].strip()
        return forget(rest)

    # RECALL ALL
    if any(w in text for w in ["what do you know", "recall all", "show memory", "my info"]):
        return recall_all()

    # RECALL specific
    if "recall" in text:
        rest = user_input[user_input.lower().find("recall") + 6:].strip()
        return recall(rest)

    return recall_all()

# Load memory context for system prompt
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

    else:  # chat
        messages.append({"role": "user", "content": user_input})
        response = ask_ollama(messages)
        messages.append({"role": "assistant", "content": response})
        print(f"\n[AutoAgent]: {response}")
        add_history("user", user_input)
        add_history("assistant", response)