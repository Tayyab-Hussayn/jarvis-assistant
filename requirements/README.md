# JARVIS Requirements Directory

This directory contains component-specific requirement files for modular installation.

## 📁 Component Requirements

| File | Component | Purpose |
|------|-----------|---------|
| `requirements_db.txt` | Database System | PostgreSQL, Redis, Qdrant dependencies |
| `requirements_llm.txt` | LLM Integration | Multi-provider AI model dependencies |
| `requirements_temporal.txt` | Workflow Engine | Temporal.io enterprise workflows |
| `requirements_voice.txt` | Voice System | TTS/STT and audio processing |
| `requirements_web.txt` | Web Automation | Playwright browser automation |

## 🚀 Installation Options

### Full Installation (Recommended)
```bash
# Install all dependencies
pip install -r requirements.txt
```

### Modular Installation
```bash
# Install only specific components
pip install -r requirements/requirements_llm.txt
pip install -r requirements/requirements_db.txt
pip install -r requirements/requirements_temporal.txt
pip install -r requirements/requirements_voice.txt
pip install -r requirements/requirements_web.txt
```

### Minimal Installation
```bash
# Core system only (LLM + basic functionality)
pip install -r requirements/requirements_llm.txt
```

## 📋 Post-Installation Steps

```bash
# Install browser binaries (if using web automation)
playwright install

# Create environment configuration
python config_cli.py create-env

# Set environment variables in .env file
# LLM_API_KEY=your_api_key_here
```

## 🎯 Production Deployment

```bash
# Full production setup
pip install -r requirements.txt
playwright install --with-deps
python config_cli.py create-env
# Configure .env file with production settings
```
