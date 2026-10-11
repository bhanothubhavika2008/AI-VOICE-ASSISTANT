from flask import Flask, render_template, request, jsonify
import os, platform, subprocess, webbrowser, urllib.parse, re, time

app = Flask(__name__)
SYSTEM = platform.system().lower()

# Only explicitly allowed actions are exposed. Voice text is never passed to a shell.
APP_ALIASES = {
    "notepad": {"windows": ["notepad.exe"], "linux": ["gedit"], "darwin": ["open", "-a", "TextEdit"]},
    "calculator": {"windows": ["calc.exe"], "linux": ["gnome-calculator"], "darwin": ["open", "-a", "Calculator"]},
    "paint": {"windows": ["mspaint.exe"], "linux": ["pinta"], "darwin": ["open", "-a", "Preview"]},
    "file explorer": {"windows": ["explorer.exe"], "linux": ["xdg-open", os.path.expanduser("~")], "darwin": ["open", os.path.expanduser("~")]},
}


def platform_key():
    return "windows" if SYSTEM == "windows" else ("darwin" if SYSTEM == "darwin" else "linux")


def keyboard():
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        return pyautogui
    except Exception as exc:
        raise RuntimeError("PC automation library is unavailable. Install dependencies and run on your desktop session.") from exc


def set_volume(direction):
    if SYSTEM == "windows":
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            target = min(1.0, current + 0.10) if direction == "up" else max(0.0, current - 0.10)
            volume.SetMasterVolumeLevelScalar(target, None)
            return f"System volume set to about {round(target * 100)}%."
        except Exception:
            # Keyboard media keys are a useful fallback on Windows.
            pyautogui = keyboard()
            key = "volumeup" if direction == "up" else "volumedown"
            for _ in range(3): pyautogui.press(key)
            return "Sent system volume key presses."
    pyautogui = keyboard()
    key = "volumeup" if direction == "up" else "volumedown"
    for _ in range(3): pyautogui.press(key)
    return "Sent volume key presses. Exact system volume support depends on your desktop environment."


def execute_command(raw):
    if not isinstance(raw, str) or not raw.strip():
        return {"ok": False, "message": "Please say or type a command."}
    text = re.sub(r"\s+", " ", raw.strip().lower())

    # Launch only named, allowlisted applications; never run arbitrary user-provided commands.
    for alias, commands in APP_ALIASES.items():
        if text in (f"open {alias}", f"launch {alias}", f"start {alias}", alias):
            args = commands.get(platform_key())
            if not args:
                return {"ok": False, "message": f"Opening {alias} is not configured for this operating system."}
            try:
                subprocess.Popen(args, shell=False)
                return {"ok": True, "message": f"Opening {alias.title()} on your PC."}
            except FileNotFoundError:
                return {"ok": False, "message": f"Could not find {alias.title()}. It may not be installed on this PC."}
            except Exception as exc:
                return {"ok": False, "message": f"Could not open {alias.title()}: {exc}"}

    if text in ("scroll down", "scroll up", "page down", "page up"):
        pyautogui = keyboard()
        if text == "scroll down": pyautogui.scroll(-5)
        elif text == "scroll up": pyautogui.scroll(5)
        elif text == "page down": pyautogui.press("pagedown")
        else: pyautogui.press("pageup")
        return {"ok": True, "message": f"Executed {text}."}

    if text in ("go back", "back", "previous page"):
        keyboard().hotkey("alt", "left")
        return {"ok": True, "message": "Navigated back."}
    if text in ("go forward", "forward", "next page"):
        keyboard().hotkey("alt", "right")
        return {"ok": True, "message": "Navigated forward."}
    if text in ("refresh", "refresh page"):
        keyboard().hotkey("ctrl", "r")
        return {"ok": True, "message": "Refreshed the current page or window."}

    if text in ("increase volume", "volume up", "turn volume up", "raise volume"):
        return {"ok": True, "message": set_volume("up")}
    if text in ("decrease volume", "volume down", "turn volume down", "lower volume"):
        return {"ok": True, "message": set_volume("down")}
    if text in ("mute", "mute volume"):
        keyboard().press("volumemute")
        return {"ok": True, "message": "Sent the system mute key."}

    # Search uses the default browser and URL-encodes the query; it does not type into a shell.
    prefixes = ("search for ", "search ", "google ", "look up ")
    for prefix in prefixes:
        if text.startswith(prefix) and text[len(prefix):].strip():
            query = text[len(prefix):].strip()
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            webbrowser.open(url, new=2)
            return {"ok": True, "message": f"Searching the web for: {query}"}

    return {"ok": False, "message": "Command not recognized. Try one of the listed commands."}


@app.get("/")
def index():
    return render_template("index.html", os_name=platform.system())

@app.get("/api/status")
def status():
    return jsonify({"ok": True, "os": platform.system(), "mode": "real-local-control", "commands": [
        "Open Notepad", "Open Calculator", "Open Paint", "Open File Explorer",
        "Scroll down", "Scroll up", "Page down", "Page up", "Search for cats",
        "Increase volume", "Decrease volume", "Mute", "Go back", "Go forward", "Refresh"
    ]})

@app.post("/api/command")
def command():
    body = request.get_json(silent=True) or {}
    try:
        result = execute_command(body.get("command", ""))
        return jsonify(result), (200 if result.get("ok") else 400)
    except Exception as exc:
        return jsonify({"ok": False, "message": str(exc)}), 500

if __name__ == "__main__":
    # localhost only: the API is intentionally not exposed to other devices on the network.
    app.run(host="127.0.0.1", port=5000, debug=False)
