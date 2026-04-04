import os
import shutil

def handle_file_command(user_input: str) -> str:
    text = user_input.lower()

    # LIST
    if any(w in text for w in ["list", "show files", "ls", "dir"]):
        path = "."
        try:
            items = os.listdir(path)
            return "\n".join(items) if items else "Folder is empty."
        except Exception as e:
            return f"Error: {e}"

    # READ
    if "read" in text or "open" in text and "file" in text:
        words = user_input.split()
        for word in words:
            if os.path.isfile(word):
                with open(word, "r") as f:
                    return f.read()
        return "Please specify a valid filename. E.g: read notes.txt"

    # CREATE
    if "create" in text or "make file" in text or "new file" in text:
        words = user_input.split()
        for word in words:
            if "." in word and "/" not in word:
                with open(word, "w") as f:
                    f.write("")
                return f"Created file: {word}"
        return "Please specify a filename. E.g: create notes.txt"

    # DELETE
    if "delete" in text or "remove" in text:
        words = user_input.split()
        for word in words:
            if os.path.isfile(word):
                os.remove(word)
                return f"Deleted: {word}"
            elif os.path.isdir(word):
                shutil.rmtree(word)
                return f"Deleted folder: {word}"
        return "Please specify a valid file or folder name."

    # WRITE
    if "write" in text and "file" in text:
        return "Tell me the filename and content. E.g: write to notes.txt: Hello World"

    return "File command not understood. Try: list, read <file>, create <file>, delete <file>"