import requests

def classify_intent(user_input: str) -> str:
    prompt = f"""Classify this input into exactly one category.

Categories:
- code     : write, run, debug, explain, or fix code
- file     : create, read, write, delete, list files
- app      : open, launch, or close an application
- search   : search web, find current info or news
- memory   : remember, recall, forget personal facts
- organize : organize folder, clean screenshots, find duplicates, analyze disk, sort files
- chat     : explain concepts, general knowledge, conversation

Rules:
- "organize my downloads" → organize
- "clean screenshots" → organize
- "find duplicate files" → organize
- "how much disk space" → organize
- "sort files in folder" → organize
- "what is X" → chat
- "search X" → search
- "open X" → app
- "write code" → code
- "list files" → file
- "remember X" → memory

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

    if result not in ("code", "file", "app", "search", "memory", "organize", "chat"):
        return "chat"
    return result