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

def fmt_size(b: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"

def disk_usage(folder_path: str) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    category_sizes = {}
    total = 0

    for file in folder.rglob("*"):
        if not file.is_file():
            continue
        try:
            size = file.stat().st_size
        except Exception:
            continue
        category = get_category(file.suffix)
        category_sizes[category] = category_sizes.get(category, 0) + size
        total += size

    if total == 0:
        return "Folder is empty."

    lines = [
        f"Disk usage: {folder_path}",
        f"Total: {fmt_size(total)}",
        ""
    ]
    for cat, size in sorted(category_sizes.items(), key=lambda x: -x[1]):
        pct = (size / total * 100)
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)
        lines.append(f"{cat:<12} {bar} {fmt_size(size):>10} ({pct:.1f}%)")

    return "\n".join(lines)

def folder_summary(folder_path: str) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    files = [f for f in folder.rglob("*") if f.is_file()]
    folders = [f for f in folder.rglob("*") if f.is_dir()]

    total_size = 0
    for f in files:
        try:
            total_size += f.stat().st_size
        except Exception:
            continue

    lines = [
        f"Folder:  {folder_path}",
        f"Files:   {len(files)}",
        f"Folders: {len(folders)}",
        f"Size:    {fmt_size(total_size)}",
    ]

    if files:
        try:
            newest = max(files, key=lambda f: f.stat().st_mtime)
            oldest = min(files, key=lambda f: f.stat().st_mtime)
            lines.append(f"Newest:  {newest.name} ({datetime.fromtimestamp(newest.stat().st_mtime).strftime('%Y-%m-%d')})")
            lines.append(f"Oldest:  {oldest.name} ({datetime.fromtimestamp(oldest.stat().st_mtime).strftime('%Y-%m-%d')})")
        except Exception:
            pass

    return "\n".join(lines)