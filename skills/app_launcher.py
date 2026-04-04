import subprocess
import os

APP_MAP = {
    "chrome":    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox":   r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "vscode":    r"C:\Users\mufee\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "vs code":   r"C:\Users\mufee\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "notepad":   "notepad.exe",
    "calculator":"calc.exe",
    "explorer":  "explorer.exe",
    "spotify":   r"C:\Users\mufee\AppData\Roaming\Spotify\Spotify.exe",
    "terminal":  "wt.exe",
    "cmd":       "cmd.exe",
    "taskmgr":   "taskmgr.exe",
    "settings":  "ms-settings:",
}

def handle_app_command(user_input: str) -> str:
    text = user_input.lower()

    for app_name, app_path in APP_MAP.items():
        if app_name in text:
            try:
                if app_path.startswith("ms-"):
                    os.startfile(app_path)
                else:
                    subprocess.Popen([app_path])
                return f"Launched: {app_name}"
            except FileNotFoundError:
                return f"Could not find {app_name} at path: {app_path}. Update APP_MAP in app_launcher.py"
            except Exception as e:
                return f"Error launching {app_name}: {e}"

    return "App not recognized. Add it to APP_MAP in skills/app_launcher.py"