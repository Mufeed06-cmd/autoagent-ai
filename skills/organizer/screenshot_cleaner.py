from pathlib import Path
from datetime import datetime

SCREENSHOT_KEYWORDS = ["screenshot", "screen shot", "capture", "snap", "scr"]
IMAGE_EXTS = [".png", ".jpg", ".jpeg", ".bmp"]

def clean_screenshots(
    folder_path: str,
    days_old: int = 30,
    dry_run: bool = False
) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    now = datetime.now().timestamp()
    cutoff = days_old * 86400
    found = []

    for file in folder.rglob("*"):
        if not file.is_file():
            continue
        if file.suffix.lower() not in IMAGE_EXTS:
            continue

        name_lower = file.name.lower()
        is_screenshot = any(kw in name_lower for kw in SCREENSHOT_KEYWORDS)

        try:
            is_old = (now - file.stat().st_mtime) > cutoff
        except Exception:
            continue

        if is_screenshot and is_old:
            if not dry_run:
                try:
                    file.unlink()
                    found.append(f"  Deleted: {file.name}")
                except Exception as e:
                    found.append(f"  Failed: {file.name} — {e}")
            else:
                found.append(f"  Would delete: {file.name}")

    if not found:
        return f"No old screenshots found (older than {days_old} days)."

    label = "DRY RUN" if dry_run else "CLEANED"
    return f"[{label}] {len(found)} screenshot(s):\n" + "\n".join(found)