# 🌌 AUI — Artificial User Interface

**AUI** is a sleek, modern, AI-powered chat client built with **PyQt5** and themed using **Gruvbox** for a polished user experience. Designed for local usage with support for the **Gemini API**, it offers a customizable, fluid, and beautiful desktop AI chat environment — right on your system.

![aui-preview](preview.png)

---

## ✨ Features

- 📜 Markdown-supported messages
- 🎨 Beautiful, themed chat UI (Gruvbox, Monokai, Catppuccin, etc.)
- 🧵 Chat bubbles aligned (left for AI, right for user)
- 💬 Chat history with session management
- ⚙️ Settings panel with:
  - Font selection and scaling
  - Theme switching
  - API Key storage
- ⌨️ Keyboard Shortcuts:
  - `Ctrl+Enter` to send message
- 📝 Message input area always docked to bottom
- 💾 Auto-saving chat sessions
- 📘 Info tab for usage guidance
- 💬 Built-in motivational and taunting quotes from **Bennett Foddy**
- 🧊 Smooth animations, UI feedback, and stylized interactions

---

## 🛠 Installation

### 📦 Requirements

- Python 3.8+
- `PyQt5`
- `markdown`
- Gemini API Key (optional for offline use)

Install dependencies:

```bash
pip install -r requirements.txt
```

**`requirements.txt`**:
```txt
PyQt5>=5.15
markdown
```

---

## 🚀 Running AUI

```bash
python aui.py
```

---

## 🏗️ Building a Standalone App

### Using PyInstaller (Linux & Windows):

```bash
pyinstaller --onefile --windowed aui.py
strip dist/AUI         # Optional: strip debug symbols
upx --best --lzma dist/AUI  # Optional: compress with UPX
```

> Note: `--onefile` is slower to launch due to extraction. Use `--onedir` for faster startup.

---

### 💡 Optional: Faster Native Build with Nuitka (Recommended)

Install Nuitka:

```bash
pip install nuitka
```

Compile:

```bash
nuitka --standalone --enable-plugin=pyqt5 --output-dir=build aui.py
```

This generates a **fast native binary**.

---

## 🖥️ Cross-Platform Notes

- ✅ Works on **Linux**
- 🚫 macOS not tested, but can work with PyQt5 and PyInstaller
- 🚫 windows not tested
---

## 📁 Chat Saving

Chat sessions are stored in the local `./history/` folder as plain `.txt` files. These are loaded dynamically into the history tab for each session.

---

## 💡 Info Tab

The built-in Info tab guides users on:

- Keyboard shortcuts
- API setup
- Customization tips
- Where chat sessions are saved
- Theme and font support

---

## 🎨 Customization

AUI supports:

- Font selection from installed system fonts
- Font size scaling and UI zoom
- Switchable themes with dark/light variants
- Toggle settings and chat history via UI buttons

---

## ❓ How to Use

- Type your prompt in the input box at the bottom
- Hit `Ctrl+Enter` or click "Send"
- View Gemini's responses in styled chat bubbles
- Switch between tabs to view:
  - Chat
  - Settings
  - History
  - Info

---

## 💬 Quote Mode

While the responses are being generated , you can read the quote that AUI has to say to you , as geenrating messeges can take long time depending on how big response is
Example:
> “You can't skip the hard parts — that's the whole point.”

---

## 🧠 AI Integration

AUI uses the **Gemini API** for generating responses.
To enable it:
1. Go to the **Settings** tab
2. Enter your API Key in the text box
3. Save — your key will be used in future sessions

---
---

## 📜 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

---

## ✨ Credits

- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- [Markdown](https://python-markdown.github.io/)
- [Google Gemini API](https://ai.google.dev/)
- UI & design by [Joy](https://github.com/skubed0007)

---