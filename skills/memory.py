import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memory.json")

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"facts": {}, "history": []}

def save_memory(memory: dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def remember(key: str, value: str):
    memory = load_memory()
    memory["facts"][key] = value
    save_memory(memory)
    return f"Remembered: {key} = {value}"

def recall(key: str) -> str:
    memory = load_memory()
    value = memory["facts"].get(key)
    if value:
        return f"{key}: {value}"
    return f"Nothing remembered for '{key}'"

def recall_all() -> str:
    memory = load_memory()
    facts = memory["facts"]
    if not facts:
        return "No memories stored yet."
    return "\n".join([f"- {k}: {v}" for k, v in facts.items()])

def forget(key: str) -> str:
    memory = load_memory()
    if key in memory["facts"]:
        del memory["facts"][key]
        save_memory(memory)
        return f"Forgot: {key}"
    return f"Nothing found for '{key}'"

def add_history(role: str, content: str):
    memory = load_memory()
    memory["history"].append({
        "role": role,
        "content": content,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep only last 50 messages
    memory["history"] = memory["history"][-50:]
    save_memory(memory)

def get_history() -> list:
    memory = load_memory()
    return memory.get("history", [])