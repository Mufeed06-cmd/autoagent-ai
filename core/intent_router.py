import requests

def classify_intent(user_input: str) -> str:
    prompt = f"""Classify this input into exactly one category.

Categories:
- code   : write, run, debug, explain, or fix code in any language
- file   : create, read, write, delete, list files or folders
- app    : open, launch, or close an application or program
- search : find current info, news, facts about real people/events (starts with "search")
- chat   : explain concepts, definitions, general knowledge, conversation

Rules:
- "what is X", "explain X", "how does X work" → chat
- "search X", "find info on X", "latest news on X" → search
- "open X", "launch X" → app
- "write a X program", "debug this code" → code
- "list files", "create file", "delete X" → file

Respond with ONLY the category word.

Input: {user_input}
Category:"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5-coder:7b",
        "prompt": prompt,
        "stream": False
    })

    result = response.json()["response"].strip().lower()

    # Extract first word only in case model adds extra text
    result = result.split()[0] if result.split() else "chat"

    if result not in ("code", "file", "app", "search", "chat"):
        return "chat"
    return result