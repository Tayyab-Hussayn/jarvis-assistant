# JARVIS Configuration System Guide

## 🎯 Overview

JARVIS uses a sophisticated configuration management system that supports multiple environments, environment variables, and secure secret management.

## 🏗️ Configuration Structure

```
config/
├── environments/
│   ├── development.yaml    # Development settings
│   ├── production.yaml     # Production settings
│   └── testing.yaml        # Testing settings
└── .env                    # Environment variables (local)
```

## 🌍 Environment Management

### Setting Environment
```bash
# Set environment variable
export JARVIS_ENV=development  # or production, testing

# Or use the CLI
python config_cli.py set-env development
```

### Environment-Specific Settings

#### Development (default)
- Local database (SQLite)
- Debug logging enabled
- Relaxed security settings
- Local Temporal server

#### Production
- External database (PostgreSQL)
- Info-level logging
- Strict security settings
- Production Temporal cluster

#### Testing
- In-memory database
- Debug logging
- Mock services enabled
- Isolated test environment

## 🔧 Configuration CLI

### Available Commands

```bash
# Show current configuration
python config_cli.py show

# Validate configuration
python config_cli.py validate

# Test configuration loading
python config_cli.py test

# Set environment
python config_cli.py set-env production

# Create .env file from template
python config_cli.py create-env
```

### Example Usage

```bash
# Check current settings
$ python config_cli.py show
🔧 JARVIS Configuration
========================================
Environment: development

📡 Temporal:
  Address: localhost:7233
  Timeout: 3600s
  Task Queue: jarvis-dev-queue

🤖 LLM:
  Provider: qwen
  Model: qwen2.5-coder:7b
  API Key: Not Set
  Max Tokens: 4096
```

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JARVIS_ENV` | Environment name | `development` |
| `LLM_API_KEY` | LLM provider API key | `sk-...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EMAIL_USERNAME` | Email account username | - |
| `EMAIL_PASSWORD` | Email account password | - |
| `TEMPORAL_ADDRESS` | Temporal server address | `localhost:7233` |
| `DATABASE_URL` | Database connection URL | SQLite file |

### Setting Variables

#### Method 1: .env File
```bash
# Create .env file
python config_cli.py create-env

# Edit .env file
nano .env
```

#### Method 2: Export Commands
```bash
export JARVIS_ENV=production
export LLM_API_KEY=your_api_key_here
export EMAIL_USERNAME=your_email@gmail.com
```

#### Method 3: System Environment
Add to `~/.bashrc` or `~/.profile`:
```bash
export JARVIS_ENV=development
export LLM_API_KEY=your_api_key_here
```

## ⚙️ Configuration Sections

### Temporal Settings
```yaml
temporal:
  address: "localhost:7233"        # Server address
  timeout: 3600                    # Workflow timeout (seconds)
  task_queue: "jarvis-dev-queue"   # Task queue name
```

### LLM Settings
```yaml
llm:
  provider: "qwen"                 # Provider name
  api_key: "${LLM_API_KEY}"       # API key from env var
  model: "qwen2.5-coder:7b"       # Model name
  max_tokens: 4096                # Maximum tokens per request
```

### Database Settings
```yaml
database:
  url: "sqlite:///jarvis_dev.db"  # Database URL
  pool_size: 5                    # Connection pool size
```

### Email Settings
```yaml
email:
  smtp_server: "smtp.gmail.com"   # SMTP server
  smtp_port: 587                  # SMTP port
  username: "${EMAIL_USERNAME}"   # Username from env var
  password: "${EMAIL_PASSWORD}"   # Password from env var
```

### Voice Settings
```yaml
voice:
  tts_enabled: true               # Text-to-speech enabled
  stt_enabled: true               # Speech-to-text enabled
  voice_speed: 1.0                # Speech speed multiplier
```

### Monitoring Settings
```yaml
monitoring:
  enabled: false                  # Monitoring enabled
  log_level: "DEBUG"              # Log level
  metrics_port: 9090              # Metrics server port
```

### Security Settings
```yaml
security:
  allowed_commands: ["echo", "ls", "pwd", "cat"]  # Allowed shell commands
  sandbox_enabled: true           # Sandbox mode enabled
  max_execution_time: 300         # Max execution time (seconds)
```

## 🔄 Configuration Loading Process

1. **Environment Detection**: Check `JARVIS_ENV` variable
2. **File Loading**: Load `config/environments/{environment}.yaml`
3. **Variable Substitution**: Replace `${VAR_NAME}` with environment variables
4. **Validation**: Validate all required settings
5. **Object Creation**: Create configuration object

## 🛠️ Troubleshooting

### Common Issues

#### Configuration Not Loading
```bash
# Check environment
echo $JARVIS_ENV

# Validate configuration
python config_cli.py validate

# Test loading
python config_cli.py test
```

#### Missing Environment Variables
```bash
# Check which variables are missing
python config_cli.py show

# Set missing variables
export LLM_API_KEY=your_key_here
```

#### Invalid Configuration
```bash
# Validate configuration syntax
python config_cli.py validate

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/environments/development.yaml'))"
```

### Error Messages

#### "Environment variable 'X' not found"
- **Cause**: Required environment variable not set
- **Solution**: Set the variable or add to .env file

#### "Config file not found"
- **Cause**: Environment file missing
- **Solution**: Check file exists in `config/environments/`

#### "Validation failed"
- **Cause**: Invalid configuration values
- **Solution**: Check required fields and data types

## 🎯 Best Practices

### Security
- Never commit API keys to version control
- Use environment variables for secrets
- Rotate API keys regularly
- Use different keys for different environments

### Organization
- Keep environment-specific settings in separate files
- Use descriptive variable names
- Document configuration changes
- Test configuration changes in development first

### Maintenance
- Regularly review configuration settings
- Update default values as needed
- Monitor for deprecated settings
- Keep documentation up to date

## 📋 Configuration Checklist

### Development Setup
- [ ] Set `JARVIS_ENV=development`
- [ ] Configure LLM API key
- [ ] Test configuration loading
- [ ] Verify all services start correctly

### Production Deployment
- [ ] Set `JARVIS_ENV=production`
- [ ] Configure production database
- [ ] Set all required environment variables
- [ ] Test configuration validation
- [ ] Verify security settings
- [ ] Test service connectivity

---
*For monitoring configuration, see monitoring/monitoring_guide.md*
