import requests

def classify_intent(user_input: str) -> str:
    """
    Returns one of: code | file | app | chat
    """
    prompt = f"""Classify the following user input into exactly one category.
Categories:
- code : user wants to write, run, debug, or explain code
- file : user wants to create, read, write, delete, or list files/folders
- app  : user wants to open, close, or launch an application
- chat : general question or conversation

Respond with ONLY the category word. Nothing else.

Input: {user_input}
Category:"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5-coder:7b",
        "prompt": prompt,
        "stream": False
    })
    
    result = response.json()["response"].strip().lower()
    
    # Sanitize — fallback to chat if unexpected
    if result not in ("code", "file", "app", "chat"):
        return "chat"
    return result