import shutil
from pathlib import Path
from datetime import datetime

FILE_CATEGORIES = {
    "Images":     [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico", ".tiff"],
    "Videos":     [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "Audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"],
    "Documents":  [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt"],
    "Code":       [".py", ".js", ".ts", ".html", ".css", ".c", ".cpp", ".java", ".json", ".xml", ".sh", ".bat"],
    "Archives":   [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "Executables":[".exe", ".msi", ".apk"],
    "Data":       [".csv", ".sql", ".db", ".sqlite"],
    "Others":     []
}

def get_category(ext: str) -> str:
    ext = ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"

def organize_folder(folder_path: str, dry_run: bool = False) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    moved = []

    for file in folder.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix
        category = get_category(ext)
        dest_folder = folder / category

        if not dry_run:
            dest_folder.mkdir(exist_ok=True)
            dest = dest_folder / file.name
            if dest.exists():
                dest = dest_folder / f"{file.stem}_{datetime.now().strftime('%H%M%S')}{ext}"
            try:
                shutil.move(str(file), str(dest))
                moved.append(f"  {file.name} → {category}/")
            except Exception as e:
                moved.append(f"  FAILED: {file.name} — {e}")
        else:
            moved.append(f"  {file.name} → {category}/ [preview]")

    if not moved:
        return "No files to organize."

    label = "PREVIEW" if dry_run else "DONE"
    return f"[{label}] {len(moved)} files:\n" + "\n".join(moved)