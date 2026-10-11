# VOICE. THINK. AUTOMATE. — runnable local prototype

A local Flask website with browser-based online speech recognition and a Python backend that performs real, allowlisted desktop actions. The included command set is intentionally small and safe. This is a prototype, not a general-purpose AI agent.

## Requirements
- Windows 10/11 recommended for the provided app aliases and volume control
- Python 3.10 or newer
- Recent Google Chrome or Microsoft Edge for Web Speech Recognition
- Internet connection for online browser speech recognition and web search

## Setup (Windows)
1. Extract this folder to a normal folder such as `C:\voice_think_automate`.
2. Open Command Prompt or PowerShell in that folder.
3. Create a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt and run `.venv\Scripts\activate.bat` instead.
4. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Start the local server:
   ```powershell
   python app.py
   ```
6. Open **http://127.0.0.1:5000** in Chrome or Edge. Allow microphone permission when prompted.
7. Keep the terminal/server running while you use the assistant. The browser tab can be in front when using scroll/navigation commands, because those actions affect the currently focused desktop window.

## Commands to demo
Say or type these exactly:
- `Open Notepad`
- `Open Calculator`
- `Open Paint`
- `Open File Explorer`
- `Scroll down` / `Scroll up`
- `Page down` / `Page up`
- `Search for artificial intelligence`
- `Increase volume` / `Decrease volume` / `Mute`
- `Go back` / `Go forward` / `Refresh`

Use the typed command field first to test that the local backend and OS permissions work; then test microphone recognition.

## Important behavior and safety
- The browser uses its built-in Web Speech API for **online** speech recognition. Browser support and recognition service availability vary. Chrome/Edge are recommended; the mic button is disabled when the API is unavailable.
- Real PC actions are run by the local Python process, not by the website alone. The server binds to `127.0.0.1` only and must run on the same computer being controlled.
- The backend does not execute arbitrary terminal commands. App launches are an explicit allowlist; command text is never passed to a shell.
- `Scroll`, page navigation, and volume-key actions use PyAutoGUI and affect the currently focused desktop session/window. Move the pointer to a safe area before testing; PyAutoGUI's fail-safe is enabled.
- On Windows, the `pycaw` volume API is attempted first. Other operating systems use media keys and may need desktop-specific configuration.
- On Linux, you may need to install a supported app for `gedit`, `gnome-calculator`, or `pinta`; change the explicit allowlist in `app.py` to match your system. macOS app mappings are examples and can be adjusted.
- Browser speech recognition and Google search require internet. Local app launching and keyboard actions run locally.
- Do not run this prototype as administrator/root. Only run it on a computer you are authorized to control.

## Troubleshooting
- **`py` not found:** install Python from python.org and select “Add Python to PATH”.
- **Microphone blocked:** browser site settings → Microphone → Allow for `127.0.0.1`, then reload.
- **Voice button unavailable:** use current Chrome/Edge; typed commands still work.
- **Actions fail:** ensure the Python server is running and use the same logged-in desktop session. Check the terminal for Python errors.
- **Notepad opens but scrolling seems ineffective:** focus a scrollable window first. Scroll commands operate on the currently focused window, not necessarily the browser.

## Project structure
```
voice_think_automate/
  app.py
  requirements.txt
  README.md
  templates/index.html
  static/style.css
  static/app.js
```
