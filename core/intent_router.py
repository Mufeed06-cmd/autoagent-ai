import requests

def classify_intent(user_input: str) -> str:
    prompt = f"""Classify this input into exactly one category.

Categories:
- code   : write, run, debug, explain, or fix code in any language
- file   : create, read, write, delete, list files or folders
- app    : open, launch, or close an application or program
- search : find current info, news, facts (starts with "search")
- memory : remember something, recall something, forget something, what do you know about me
- chat   : explain concepts, definitions, general knowledge, conversation

Rules:
- "remember my name is X" → memory
- "what do you know about me" → memory
- "recall X", "forget X" → memory
- "what is X", "explain X" → chat
- "search X" → search
- "open X" → app
- "write code" → code
- "list files" → file

Respond with ONLY the category word.

Input: {user_input}
Category:"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5-coder:7b",
        "prompt": prompt,
        "stream": False
    })

    result = response.json()["response"].strip().lower()
    result = result.split()[0] if result.split() else "chat"

    if result not in ("code", "file", "app", "search", "memory", "chat"):
        return "chat"
    return result