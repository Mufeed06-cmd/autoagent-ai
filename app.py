from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os, psutil, shutil, platform, subprocess, time, threading, json
from datetime import datetime
import send2trash, winshell, ollama

app = Flask(__name__)
CORS(app)

# ─── CONFIG ───────────────────────────────────────────────
USERNAME    = os.getlogin()
USERPROFILE = os.environ.get("USERPROFILE", f"C:\\Users\\{USERNAME}")

# Auto-detect correct paths (handles OneDrive Desktop)
DOWNLOAD_FOLDER = os.path.join(USERPROFILE, "Downloads")

DESKTOP_FOLDER = (
    os.path.join(USERPROFILE, "OneDrive", "Desktop")
    if os.path.exists(os.path.join(USERPROFILE, "OneDrive", "Desktop"))
    else os.path.join(USERPROFILE, "Desktop")
)

SCREENSHOT_FOLDER = (
    os.path.join(USERPROFILE, "OneDrive", "Documents", "Pictures", "Screenshots")
    if os.path.exists(os.path.join(USERPROFILE, "OneDrive", "Documents", "Pictures", "Screenshots"))
    else os.path.join(USERPROFILE, "OneDrive", "Pictures", "Screenshots")
    if os.path.exists(os.path.join(USERPROFILE, "OneDrive", "Pictures", "Screenshots"))
    else os.path.join(USERPROFILE, "Pictures", "Screenshots")
)

# Create Screenshots folder if it doesn't exist
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

AI_MODEL = "qwen3:8b"

FILE_CATEGORIES = {
    "Images"     : [".jpg",".jpeg",".png",".gif",".bmp",".webp",".svg"],
    "Videos"     : [".mp4",".mkv",".avi",".mov",".wmv",".flv"],
    "Audio"      : [".mp3",".wav",".aac",".flac",".ogg"],
    "Documents"  : [".pdf",".docx",".doc",".txt",".pptx",".xlsx",".csv"],
    "Archives"   : [".zip",".rar",".7z",".tar",".gz"],
    "Code"       : [".py",".js",".html",".css",".json",".ts",".cpp",".java"],
    "Executables": [".exe",".msi",".bat",".sh"],
}

action_logs = []

def log_action(action: str):
    action_logs.insert(0, {"time": datetime.now().strftime("%H:%M"), "action": action})
    if len(action_logs) > 100:
        action_logs.pop()

def folder_size_mb(path):
    total = 0
    for dp, _, files in os.walk(path):
        for f in files:
            try: total += os.path.getsize(os.path.join(dp, f))
            except: pass
    return round(total / (1024 * 1024), 1)

@app.route("/api/stats")
def stats():
    cpu  = psutil.cpu_percent(interval=0.3)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    boot = datetime.fromtimestamp(psutil.boot_time())
    ss_count = len(os.listdir(SCREENSHOT_FOLDER)) if os.path.exists(SCREENSHOT_FOLDER) else 0
    ss_mb    = folder_size_mb(SCREENSHOT_FOLDER) if os.path.exists(SCREENSHOT_FOLDER) else 0
    procs = []
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_info"]):
        try:
            ram = p.info["memory_info"].rss / (1024**2)
            if ram > 50:
                procs.append({"name": p.info["name"], "cpu": round(p.info["cpu_percent"],1),
                               "ram": f"{ram:.0f} MB" if ram < 1024 else f"{ram/1024:.1f} GB"})
        except: pass
    procs = sorted(procs, key=lambda x: float(x["ram"].replace(" MB","").replace(" GB","")), reverse=True)[:5]
    health = max(0, 100 - int(disk.percent*0.4) - int(mem.percent*0.3) - int(cpu*0.3))
    return jsonify({"cpu": round(cpu,1), "ram_percent": round(mem.percent,1),
                    "ram_used_gb": round(mem.used/1e9,1), "ram_total_gb": round(mem.total/1e9,1),
                    "disk_percent": round(disk.percent,1), "disk_used_gb": round(disk.used/1e9,1),
                    "disk_total_gb": round(disk.total/1e9,1), "disk_free_gb": round(disk.free/1e9,1),
                    "ss_count": ss_count, "ss_mb": ss_mb, "health": health,
                    "uptime": boot.strftime("%Y-%m-%d %H:%M"), "processes": procs,
                    "log_count": len(action_logs), "time": datetime.now().strftime("%I:%M %p")})

@app.route("/api/clean/screenshots", methods=["POST"])
def clean_screenshots():
    if not os.path.exists(SCREENSHOT_FOLDER):
        return jsonify({"ok": False, "msg": "Screenshot folder not found."})
    files = [f for f in os.listdir(SCREENSHOT_FOLDER) if os.path.isfile(os.path.join(SCREENSHOT_FOLDER, f))]
    if not files:
        return jsonify({"ok": True, "msg": "No screenshots found — already clean!", "count": 0})
    for f in files:
        send2trash.send2trash(os.path.join(SCREENSHOT_FOLDER, f))
    log_action(f"Cleaned {len(files)} screenshots")
    return jsonify({"ok": True, "msg": f"✅ {len(files)} screenshots moved to Recycle Bin.", "count": len(files)})

@app.route("/api/clean/recyclebin", methods=["POST"])
def empty_recycle_bin():
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        log_action("Recycle Bin emptied")
        return jsonify({"ok": True, "msg": "✅ Recycle Bin emptied successfully."})
    except Exception as e:
        return jsonify({"ok": False, "msg": f"Error: {str(e)}"})

@app.route("/api/clean/downloads", methods=["POST"])
def clean_downloads():
    if not os.path.exists(DOWNLOAD_FOLDER):
        return jsonify({"ok": False, "msg": "Downloads folder not found."})
    junk_ext = [".tmp",".log",".crdownload",".part",".cache"]
    junk = [f for f in os.listdir(DOWNLOAD_FOLDER) if any(f.endswith(e) for e in junk_ext)]
    if not junk:
        return jsonify({"ok": True, "msg": "No junk files found — Downloads is clean!", "count": 0})
    for f in junk:
        send2trash.send2trash(os.path.join(DOWNLOAD_FOLDER, f))
    log_action(f"Cleaned {len(junk)} junk files from Downloads")
    return jsonify({"ok": True, "msg": f"✅ {len(junk)} junk files cleaned.", "count": len(junk)})

@app.route("/api/organise/desktop", methods=["POST"])
def organise_desktop():
    if not os.path.exists(DESKTOP_FOLDER):
        return jsonify({"ok": False, "msg": f"Desktop not found: {DESKTOP_FOLDER}"})
    files = [f for f in os.listdir(DESKTOP_FOLDER)
             if os.path.isfile(os.path.join(DESKTOP_FOLDER, f)) and not f.endswith((".lnk",".url"))]
    if not files:
        return jsonify({"ok": True, "msg": "Desktop is already clean!", "count": 0})
    moved = 0
    dest_base = os.path.join(DESKTOP_FOLDER, "Organised")
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        cat = next((c for c, exts in FILE_CATEGORIES.items() if ext in exts), "Others")
        dest = os.path.join(dest_base, cat)
        os.makedirs(dest, exist_ok=True)
        src = os.path.join(DESKTOP_FOLDER, f)
        dst = os.path.join(dest, f)
        if not os.path.exists(dst):
            shutil.move(src, dst)
            moved += 1
    log_action(f"Organised {moved} files on Desktop")
    return jsonify({"ok": True, "msg": f"✅ {moved} files organised into subfolders.", "count": moved})

@app.route("/api/files/large")
def find_large_files():
    folder = request.args.get("folder", DOWNLOAD_FOLDER)
    threshold = int(request.args.get("mb", 100))
    large = []
    for dp, _, files in os.walk(folder):
        for f in files:
            fp = os.path.join(dp, f)
            try:
                size = os.path.getsize(fp) / (1024*1024)
                if size >= threshold:
                    large.append({"name": f, "path": fp, "size_mb": round(size,1)})
            except: pass
    large.sort(key=lambda x: x["size_mb"], reverse=True)
    return jsonify({"ok": True, "files": large[:20], "total": len(large)})

@app.route("/api/clean/full", methods=["POST"])
def full_clean():
    results = []
    if os.path.exists(SCREENSHOT_FOLDER):
        files = [f for f in os.listdir(SCREENSHOT_FOLDER) if os.path.isfile(os.path.join(SCREENSHOT_FOLDER, f))]
        for f in files: send2trash.send2trash(os.path.join(SCREENSHOT_FOLDER, f))
        results.append(f"{len(files)} screenshots cleaned")
    if os.path.exists(DOWNLOAD_FOLDER):
        junk = [f for f in os.listdir(DOWNLOAD_FOLDER) if any(f.endswith(e) for e in [".tmp",".log",".part",".cache",".crdownload"])]
        for f in junk: send2trash.send2trash(os.path.join(DOWNLOAD_FOLDER, f))
        results.append(f"{len(junk)} junk files cleaned")
    try:
        winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
        results.append("Recycle Bin emptied")
    except: pass
    log_action("Full system clean completed")
    msg = " • ".join(results) if results else "Nothing to clean!"
    return jsonify({"ok": True, "msg": f"✅ {msg}"})

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    message = data.get("message", "")
    history = data.get("history", [])
    system = {"role": "system", "content": (
        "You are AutoAgent AI, a smart Windows PC automation assistant "
        "powered by Qwen3 8B running locally. Help users with file management, "
        "system cleanup, process management, and Windows tasks. "
        "Be concise, friendly, and practical. Use emojis sparingly.")}
    messages = [system] + history + [{"role": "user", "content": message}]
    try:
        response = ollama.chat(model=AI_MODEL, messages=messages)
        reply = response["message"]["content"]
        log_action(f"AI: {message[:40]}...")
        return jsonify({"ok": True, "reply": reply})
    except Exception as e:
        return jsonify({"ok": False, "reply": f"Error connecting to Qwen: {str(e)}"})

@app.route("/api/ai/analyse", methods=["POST"])
def ai_analyse():
    cpu  = psutil.cpu_percent(interval=0.5)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    ss   = len(os.listdir(SCREENSHOT_FOLDER)) if os.path.exists(SCREENSHOT_FOLDER) else 0
    dl_mb = folder_size_mb(DOWNLOAD_FOLDER) if os.path.exists(DOWNLOAD_FOLDER) else 0
    prompt = f"""My Windows PC status:
- CPU: {cpu}% | RAM: {mem.percent}% ({mem.used/1e9:.1f}/{mem.total/1e9:.1f} GB)
- Disk C: {disk.percent}% used ({disk.free/1e9:.1f} GB free)
- Screenshots waiting: {ss} files
- Downloads folder: {dl_mb} MB
Give me 3 quick bullet point recommendations. Be very concise."""
    try:
        response = ollama.chat(model=AI_MODEL, messages=[{"role":"user","content":prompt}])
        return jsonify({"ok": True, "reply": response["message"]["content"]})
    except Exception as e:
        return jsonify({"ok": False, "reply": str(e)})

@app.route("/api/logs")
def get_logs():
    return jsonify({"logs": action_logs[:20], "total": len(action_logs)})

@app.route("/api/debug")
def debug():
    return jsonify({
        "username": USERNAME, "userprofile": USERPROFILE,
        "downloads": DOWNLOAD_FOLDER, "downloads_exists": os.path.exists(DOWNLOAD_FOLDER),
        "desktop": DESKTOP_FOLDER, "desktop_exists": os.path.exists(DESKTOP_FOLDER),
        "screenshots": SCREENSHOT_FOLDER, "screenshots_exists": os.path.exists(SCREENSHOT_FOLDER),
    })

@app.route("/")
def index():
    return render_template("dashboard.html")

if __name__ == "__main__":
    print("🤖 AutoAgent AI Backend starting...")
    print(f"   Model      : {AI_MODEL}")
    print(f"   Downloads  : {DOWNLOAD_FOLDER}")
    print(f"   Desktop    : {DESKTOP_FOLDER}")
    print(f"   Screenshots: {SCREENSHOT_FOLDER}")
    print(f"   URL        : http://localhost:5000")
    app.run(debug=False, port=5000)