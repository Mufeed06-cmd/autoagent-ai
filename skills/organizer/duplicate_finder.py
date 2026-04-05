import hashlib
from pathlib import Path

def get_file_hash(filepath: str) -> str:
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            buf = f.read(65536)  # Only first 64KB for speed
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return ""

def find_duplicates(folder_path: str, max_files: int = 500) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    hashes = {}
    duplicates = []
    scanned = 0

    print(f"[Librarian] Scanning (max {max_files} files)...")

    for file in folder.rglob("*"):
        if not file.is_file():
            continue
        if scanned >= max_files:
            print(f"[Librarian] Limit reached ({max_files} files scanned)")
            break

        h = get_file_hash(str(file))
        if not h:
            continue

        if h in hashes:
            duplicates.append(
                f"  DUPLICATE: {file.name}\n"
                f"  ORIGINAL:  {hashes[h]}"
            )
        else:
            hashes[h] = file.name

        scanned += 1
        if scanned % 50 == 0:
            print(f"[Librarian] Scanned {scanned} files...")

    if not duplicates:
        return f"No duplicates found (scanned {scanned} files)"

    return (
        f"Found {len(duplicates)} duplicate(s) in {scanned} files:\n\n"
        + "\n\n".join(duplicates)
    )

def delete_duplicates(folder_path: str, max_files: int = 500) -> str:
    folder = Path(folder_path)
    if not folder.exists():
        return f"Folder not found: {folder_path}"

    hashes = {}
    deleted = []
    scanned = 0

    print(f"[Librarian] Scanning for duplicates (max {max_files} files)...")

    for file in folder.rglob("*"):
        if not file.is_file():
            continue
        if scanned >= max_files:
            break

        h = get_file_hash(str(file))
        if not h:
            continue

        if h in hashes:
            try:
                file.unlink()
                deleted.append(f"  Deleted: {file.name}")
            except Exception as e:
                deleted.append(f"  Failed: {file.name} — {e}")
        else:
            hashes[h] = file.name

        scanned += 1

    if not deleted:
        return f"No duplicates found (scanned {scanned} files)"

    return (
        f"Deleted {len(deleted)} duplicate(s):\n"
        + "\n".join(deleted)
    )