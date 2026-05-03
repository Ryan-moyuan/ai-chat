# ai-chat
[README.md](https://github.com/user-attachments/files/27313857/README.md)

# AI Desktop Assistant

A cross-platform AI desktop application with Chat, Image Generation, and Knowledge Base capabilities.

**Supports both Cloud API and Local AI (Ollama) - Free to use!**

## Features

- **Chat** - Cloud API (Anthropic/Aliyun) or Local Ollama models (free, offline)
- **Image Generation** - Support for Local SD, DALL-E 3, and Stability AI
- **Knowledge Base** - RAG-powered document retrieval (PDF/TXT/DOCX)
- **Multi-language** - English, 中文，日本語
- **Conversation History** - SQLite-backed persistent storage
- **Feedback System** - Rate AI responses with thumbs up/down

## Quick Start

### Option 1: Cloud API (Paid, requires internet)

1. Get API Key from [Anthropic](https://console.anthropic.com/) or Aliyun DashScope
2. Run the app and enter your API Key in the setup dialog

### Option 2: Ollama Local AI (Free, offline)

1. Install Ollama:
   ```bash
   brew install ollama
   ollama pull qwen2.5:7b
   ```

2. Run the app and select "Ollama Local Mode" in the setup dialog

### Install & Run

```bash
pip3 install -r requirements.txt
./start.sh
# or
python3 main.py
```

## Configuration

Edit `config.json`:

```json
{
  "use_ollama": false,
  "ollama_url": "http://localhost:11434",
  "ollama_model": "qwen2.5:7b",
  "anthropic_api_key": "sk-ant-...",
  "claude_model": "claude-sonnet-4-20250514",
  "image_provider": "dalle",
  "language": "en",
  "theme": "dark"
}
```

| Option | Description | Default |
|--------|-------------|---------|
| `use_ollama` | Use local Ollama instead of API | `false` |
| `ollama_url` | Ollama server URL | `http://localhost:11434` |
| `ollama_model` | Ollama model name | `qwen2.5:7b` |
| `anthropic_api_key` | API Key (if not using Ollama) | Empty |
| `claude_model` | Model name for API mode | `claude-sonnet-4-20250514` |
| `image_provider` | `local` / `dalle` / `stability` | `dalle` |
| `language` | `en` / `zh` / `ja` | `en` |
| `theme` | `dark` / `light` / `system` | `dark` |

## Requirements

- Python 3.8+
- customtkinter 5.2+
- Anthropic SDK (for API mode)
- Pillow
- chromadb (for Knowledge Base)
- pypdf, python-docx (for document parsing)
- requests

### For Ollama (Local AI)

```bash
brew install ollama
ollama pull qwen2.5:7b  # or any other model
```

### Optional: Local Image Generation

For local Stable Diffusion:

```bash
pip3 install diffusers torch torchvision
```

## Project Structure

```
ai-desktop-app/
├── main.py              # Entry point
├── app.py               # Main window
├── config.json          # Configuration
├── requirements.txt     # Dependencies
├── start.sh             # Launch script
├── i18n.py              # Internationalization
├── core/                # Core modules
│   ├── chat_engine.py   # Chat (API + Ollama)
│   ├── memory_manager.py# Conversation storage
│   ├── image_generator.py
│   ├── rag_engine.py    # Knowledge retrieval
│   └── feedback.py      # User feedback
├── ui/                  # UI components
│   ├── chat_panel.py
│   ├── image_panel.py
│   ├── knowledge_panel.py
│   ├── settings_panel.py
│   └── setup_dialog.py  # First-run setup
└── lang/                # Translations
    ├── en.json
    ├── zh.json
    └── ja.json
```

## License

MIT License

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Supports [Anthropic Claude](https://www.anthropic.com/claude) and [Ollama](https://ollama.ai/)
- Image generation via DALL-E 3 / Stability AI / Stable Diffusion
