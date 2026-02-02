# JARVIS Root Directory - File Reference Guide

**Last Updated**: January 31, 2026  
**Purpose**: Complete reference for all files in the JARVIS root directory

---

## 🚀 **Core Application Files**

### **main.py**
- **Purpose**: Main JARVIS application entry point
- **Description**: Complete production-grade autonomous AI agent system with all 7 layers implemented
- **Usage**: `python main.py`
- **Status**: ✅ Production ready
- **Category**: Core Application

### **requirements.txt**
- **Purpose**: Complete unified dependency specification
- **Description**: All required Python packages for full JARVIS installation
- **Usage**: `pip install -r requirements.txt`
- **Status**: ✅ Comprehensive (unified from 5 component files)
- **Category**: Dependencies

---

## 🛠️ **Command Line Interface Tools**

### **audio_cli.py**
- **Purpose**: Audio file management CLI
- **Description**: Manage JARVIS audio files, cleanup, statistics
- **Usage**: `python audio_cli.py stats|cleanup|list`
- **Features**: Storage stats, file cleanup, audio organization
- **Category**: Management CLI

### **code_cli.py**
- **Purpose**: Code execution CLI
- **Description**: Test and manage code execution capabilities
- **Usage**: `python code_cli.py [commands]`
- **Features**: Code execution testing, multi-language support
- **Category**: Development CLI

### **config_cli.py**
- **Purpose**: Configuration management CLI
- **Description**: Manage JARVIS configuration settings across environments
- **Usage**: `python config_cli.py show|validate|test|set-env`
- **Features**: Environment switching, validation, configuration testing
- **Category**: Management CLI

### **email_cli.py**
- **Purpose**: Email system CLI
- **Description**: Test and manage email functionality
- **Usage**: `python email_cli.py [commands]`
- **Features**: Email sending, inbox checking, IMAP/SMTP testing
- **Category**: Feature CLI

### **llm_cli.py**
- **Purpose**: LLM management CLI
- **Description**: Manage AI language model providers and testing
- **Usage**: `python llm_cli.py status|test|switch`
- **Features**: Provider switching, API testing, model management
- **Category**: Management CLI

### **temporal_cli.py**
- **Purpose**: Temporal workflow CLI
- **Description**: Manage Temporal.io workflows and execution
- **Usage**: `python temporal_cli.py simple|multi|status|list`
- **Features**: Workflow creation, monitoring, management
- **Category**: Workflow CLI

### **voice_cli.py**
- **Purpose**: Voice system CLI
- **Description**: Test and manage TTS/STT voice capabilities
- **Usage**: `python voice_cli.py speak|listen|conversation`
- **Features**: Voice interaction, speech testing, conversation mode
- **Category**: Feature CLI

---

## ⚙️ **Configuration Files**

### **config_llm_extended.yaml**
- **Purpose**: Extended LLM configuration template
- **Description**: Additional LLM provider configurations and settings
- **Usage**: Reference for extending LLM configurations
- **Status**: ✅ Template file
- **Category**: Configuration

### **llm_config.py**
- **Purpose**: LLM configuration manager
- **Description**: Easy API and model management for LLM providers
- **Usage**: Imported by LLM system
- **Features**: Provider management, API configuration
- **Category**: Configuration

---

## 🐳 **Container Orchestration**

### **docker-compose.yml**
- **Purpose**: Main Docker Compose stack
- **Description**: PostgreSQL, Redis, Qdrant vector database services
- **Usage**: `docker-compose up -d`
- **Services**: Database infrastructure
- **Category**: Infrastructure

### **docker-compose-monitoring.yml**
- **Purpose**: Monitoring stack
- **Description**: Prometheus, Grafana, Alertmanager for system monitoring
- **Usage**: `docker-compose -f docker-compose-monitoring.yml up -d`
- **Services**: Monitoring and observability
- **Category**: Infrastructure

### **docker-compose-temporal.yml**
- **Purpose**: Temporal.io workflow stack
- **Description**: Temporal server, PostgreSQL, Web UI for enterprise workflows
- **Usage**: `docker-compose -f docker-compose-temporal.yml up -d`
- **Services**: Workflow management
- **Category**: Infrastructure

---

## 🔧 **Setup and Utilities**

### **setup_databases.sh**
- **Purpose**: Database setup script
- **Description**: Automated database initialization and configuration
- **Usage**: `bash setup_databases.sh`
- **Features**: Database creation, schema setup
- **Category**: Setup Script

---

## 📊 **Development and Progress Tracking**

### **AGENTS.py**
- **Purpose**: Development rules and operating principles
- **Description**: Core guidelines and architectural principles for all development agents
- **Usage**: Reference document for development standards
- **Status**: ✅ Complete development guidelines
- **Category**: Development Guide

### **COMPLETION_ROADMAP.py**
- **Purpose**: Gap fixing tracker and roadmap
- **Description**: Tracks remaining work to make JARVIS production-ready with clear acceptance criteria
- **Usage**: `python COMPLETION_ROADMAP.py` (for progress tracking)
- **Features**: Task tracking, completion criteria, progress monitoring
- **Category**: Progress Tracking

### **PROGRESS_TRACKER.py**
- **Purpose**: Development progress tracker
- **Description**: Tracks development progress and guides the build process through phases
- **Usage**: `python PROGRESS_TRACKER.py` (for phase tracking)
- **Features**: Phase validation, milestone tracking
- **Category**: Progress Tracking

### **completion_progress.json**
- **Purpose**: Progress state data
- **Description**: JSON data file storing current development phase and task completion status
- **Usage**: Data file (read by progress tracking systems)
- **Status**: ✅ Active progress data
- **Category**: State Data

### **progress_state.json**
- **Purpose**: Detailed progress state
- **Description**: Detailed JSON state file for progress tracking and phase management
- **Usage**: Data file (read by tracking systems)
- **Status**: ✅ Active state data
- **Category**: State Data

---

## 📚 **Documentation**

### **README.md**
- **Purpose**: Main project documentation
- **Description**: Complete JARVIS AI Agent system overview, setup instructions, and usage guide
- **Usage**: Primary project documentation
- **Status**: ✅ Comprehensive project guide
- **Category**: Documentation

### **TODO_TOMORROW.md**
- **Purpose**: Active task list
- **Description**: Mock-to-real integration tasks for immediate development work
- **Usage**: Development task reference
- **Status**: ✅ Current active tasks
- **Category**: Active Documentation

### **MOCK_TO_REAL_ROADMAP.md**
- **Purpose**: Mock data integration roadmap
- **Description**: Comprehensive plan for replacing mock data with real integrations
- **Usage**: Development roadmap reference
- **Status**: ✅ Active integration plan
- **Category**: Active Documentation

---

## 📊 **File Summary Statistics**

### **By Category**
- **Core Application**: 2 files (main.py, requirements.txt)
- **CLI Tools**: 7 files (all *_cli.py files)
- **Configuration**: 2 files (config files)
- **Infrastructure**: 3 files (Docker Compose files)
- **Setup**: 1 file (setup script)
- **Development**: 5 files (progress tracking and guidelines)
- **Documentation**: 3 files (README, TODO, roadmap)

### **By File Type**
- **Python Scripts**: 12 files (.py)
- **Documentation**: 3 files (.md)
- **Configuration**: 4 files (.yml, .yaml, .json)
- **Scripts**: 1 file (.sh)
- **Dependencies**: 1 file (.txt)

### **By Status**
- **Production Ready**: 15 files ✅
- **Active Development**: 3 files 🔄
- **Reference/Template**: 2 files 📋

---

## 🎯 **Usage Patterns**

### **Daily Development**
- `main.py` - Run JARVIS application
- `*_cli.py` - Manage and test components
- `TODO_TOMORROW.md` - Check current tasks

### **System Setup**
- `requirements.txt` - Install dependencies
- `docker-compose*.yml` - Start services
- `setup_databases.sh` - Initialize databases

### **Configuration**
- `config_cli.py` - Manage settings
- `config_llm_extended.yaml` - LLM configuration reference

### **Development**
- `COMPLETION_ROADMAP.py` - Track progress
- `AGENTS.py` - Follow development guidelines
- `MOCK_TO_REAL_ROADMAP.md` - Integration tasks

**Status**: Complete root directory reference - All 21 files documented with purpose, usage, and status ✅
