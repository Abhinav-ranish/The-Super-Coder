# VibeCode Machine - Quickstart Guide 🚀

Welcome to the VibeCode Machine!

This tool builds, tests, and auto-fixes coding projects using AI with smart patching.  
Follow these quick steps to get started:

---

## 📦 1. Setup Environment

- Python 3.8+ required
- Install dependencies:

```bash
pip install requests
```

- Make sure **Ollama** server is running locally:

```bash
ollama serve
```

- You should have a coding-capable model loaded like `codellama` or `llama3`.

---

## 🛠️ 2. Running VibeCode

```bash
python main.py
```

You'll be prompted to:

- Describe the app you want (example: `Make a simple Flask calculator app`)
- Choose whether to stream the response (recommended: `y`)

---

## 🧠 3. What Happens Next

- AI generates the app code
- Files and folders are created automatically
- Project dependencies (`requirements.txt`) are installed
- If the app requires user input, smart fake inputs are generated automatically
- App is run and tested immediately

---

## ⚠️ 4. If Errors Occur

If the app crashes:

- VibeCode will **analyze** the error
- It will **send the error + crashed file** back to AI for fixing
- If AI needs additional files, VibeCode will fetch and resend them
- A **smart patch** will be applied to only the broken functions or classes
- App will be re-tested automatically

---

## 🛡 5. Built-in Smart Features

- Standard libraries (like `math`, `sys`) are skipped during installation
- Auto-detection of missing files if AI asks for more
- Minimal correction patches applied to keep original code safe
- Supports complex multi-file projects (coming soon)

---

## 📝 6. Future Improvements (Planned)

- Auto-fixing import errors separately
- Support for full-stack app generation (React + Flask)
- Live dashboard (Tauri/Electron)
- Plugin system for custom templates
- Local file backup before applying patches

---

## 🏁 7. Congratulations

You're now vibing at the cutting-edge of autonomous AI development! 🎸

---
# Build. Test. Fix. Vibe. 🚀
