# Rudolph

A fast, minimal, cross-platform launcher built with **Python** and **PySide6**.  
It's a lightweight alternative to Raycast or Alfred — no accounts, no telemetry, just your local system and pure code.

---

## 🧠 Features

- **Smart math evaluator** — calculates expressions (with `π`, `e`, and degree support) in real-time  
- **Unit conversion** — convert between metric, imperial, and temperature units  
- **Web shortcuts** — search instantly on:
  - YouTube (`yt <query>`)
  - DuckDuckGo (`ddg <query>`)
  - Wikipedia (`wiki <query>`)
  - Perplexity (`plx <query>`)
- **Wikipedia summary fetcher** — use `wikisum <topic>` for a short extract
- **Weather lookup** — `wttr.in` integration for quick temperature and condition checks
- **Command history** — navigate previous queries with ↑ and ↓
- **Configurable hotkey** — defined in `settings.ini` (default: `super+space`)
- **Settings window** — toggle individual command modules and preferences

---

## 🛠️ Installation

### Install via pip

```bash
pip install --user rudolph-launcher
```
This will install Rudolph and rudolph-install-service in  `~/.local/bin`

Make sure `~/.local/bin` is in your PATH (use .zshrc or your shell configuration file instead of .bashrc if you use any other shell):
```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

Activate the background service: 
```bash
rudolph-install-service
```

### Install manually

### 1. Clone the repository

```bash
git clone https://github.com/guanciottaman/rudolph.git
cd rudolph
```

### 2. Set up the environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux
# or venv\Scripts\activate on Windows
pip install -r requirements.txt
```


### 3. Run the launcher

```bash
python main.py
```
### Setting up your hotkey (FOR BOTH METHODS)
On Linux, you can toggle the launcher by creating the /tmp/launcher_trigger file. Set up your hotkey:
1. Open Settings → Keyboard → Custom Shortcuts
2. Add a new shortcut:
   - Name: Rudolph Launcher
   - Command: `/home/<user>/.local/bin/rudolph`
   - Shortcut: Super+Space (or your preferred)
On Windows, the global shortcut (defined in settings.ini) will toggle it directly.
> ⚠️ On Linux: remember to set your custom shortcut manually in your desktop environment.  
> ⚠️ On Windows: the global shortcut is handled via `settings.ini`.

## 🧩 Commands Overview
| Command |	Description | Example |
| ------- | ----------- | ------- |
| e `<expression>` | Evaluate a math expression	|e 3*(2+5) |
| c `<value>` `<from>` `<to>`	| Convert units | c 10 km m |
|yt `<query>`	|Search YouTube	|yt linux tutorials|
|ddg `<query>`	|Search DuckDuckGo	|ddg python threads|
|wiki `<query>`|	Open Wikipedia page|	wiki Alan Turing|
|wikisum `<query>` |	Fetch Wikipedia summary	|wikisum Rome|
|plx `<query> `| Search on Perplexity	|plx quantum computing|

## ⚙️ Configuration

All preferences are stored in settings.ini.

```ini
[General]
shortcut = super+space
max_history = 50

[Commands]
expression = true
conversion = true
temp = true
youtube = true
google = true
duckduckgo = true
wikipedia = true
perplexity = true

```

## 🧑‍💻 Tech Stack

- Python 3.11+

- PySide6 — modern Qt bindings for UI

- numexpr — fast math expression evaluation

- requests — for network calls

- keyboard — global shortcut handling

## ⚖️ License

This project is licensed under the GPL-3.0 license.
You’re free to use, modify, and distribute it under the same license.

## ✨ Roadmap

- Plugin system for custom commands

- Custom theming & transparency

- DBus and autostart integration on Linux

Built with 🫶 by Guanciottaman