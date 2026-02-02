# JARVIS Quick Start Guide

## 🚀 Basic Usage

### Run System Demo
```bash
python main.py
```
Shows all capabilities, then exits.

### Interactive Commands

#### Voice Interface
```bash
python voice_cli.py conversation    # Start voice chat (TTS + STT)
python voice_cli.py test-speech     # Test speech recognition only
python test_jarvis_voice.py         # Test TTS integration
```

#### Task Execution
```bash
python temporal_cli.py simple "Create a Python script"
python temporal_cli.py simple "Analyze this code file" --tool file_manager
```

#### System Management
```bash
python config_cli.py show          # View configuration
python audio_cli.py stats          # Audio system status
python email_cli.py test           # Test email system
```

## 🛠️ CLI Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `voice_cli.py` | Voice interaction | `python voice_cli.py conversation` |
| `temporal_cli.py` | Task execution | `python temporal_cli.py simple "your task"` |
| `config_cli.py` | Configuration | `python config_cli.py show` |
| `audio_cli.py` | Audio management | `python audio_cli.py stats` |
| `email_cli.py` | Email testing | `python email_cli.py test` |
| `code_cli.py` | Code execution | `python code_cli.py test` |
| `llm_cli.py` | LLM management | `python llm_cli.py list` |

## 🐳 Infrastructure

### Start Services
```bash
# Database stack
docker-compose up -d

# Monitoring stack  
docker-compose -f docker-compose-monitoring.yml up -d

# Workflow engine
docker-compose -f docker-compose-temporal.yml up -d
```

### Setup Databases
```bash
./setup_databases.sh
```

## 📁 Key Files

- `main.py` - System demonstration
- `requirements.txt` - Dependencies
- `config_llm_extended.yaml` - LLM configuration
- `ROOT_DIRECTORY_GUIDE.md` - Complete file reference

## ✅ Recent Fixes

- **Voice Activity Detection**: Auto-stops 2s after silence, no time limits
- **Qwen OAuth**: Professional authentication with session management  
- **TTS Audio Playback**: Fixed audio bytes not playing through speakers
- **API Rate Limiting**: Removed custom limits, using Qwen defaults

```bash
# Voice conversation
python voice_cli.py conversation

# Execute any task
python temporal_cli.py simple "your task here"

# Check system status
python config_cli.py show
```

That's it! JARVIS is ready to use. 🤖
