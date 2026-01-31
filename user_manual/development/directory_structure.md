# JARVIS Complete Directory Structure & Code Reference

## 📁 Project Structure Overview

```
jarvis/
├── 📁 core/                    # Core system components
├── 📁 modules/                 # Modular tool system
├── 📁 config/                  # Configuration management
├── 📁 monitoring/              # Monitoring stack configs
├── 📁 user_manual/             # Documentation & guides
├── 📁 workflows/               # Workflow templates
├── 📁 skills/                  # Skills framework
├── 📁 tests/                   # Test suites
├── 📄 main.py                  # Main application entry
└── 📄 README.md                # Project overview
```

## 🏗️ Core System (`core/`)

### Engine Architecture
```
core/
├── engines/
│   ├── execution/              # Task execution engine
│   │   ├── execution_engine.py      # Main execution orchestrator
│   │   ├── parameter_mapper.py      # Tool parameter mapping
│   │   └── recovery_system.py       # Error recovery mechanisms
│   ├── reasoning/              # AI reasoning engine
│   │   └── reasoning_engine.py      # Task analysis & planning
│   └── workflow/               # Workflow management
│       ├── simple_workflow.py       # Lightweight workflow engine
│       └── enhanced_workflow.py     # Temporal.io integration
```

**Key Components:**

#### `execution_engine.py`
- **Purpose**: Orchestrates tool execution and manages task flow
- **Key Classes**: `ExecutionEngine`, `ExecutionRequest`, `ExecutionResult`
- **Features**: Tool routing, parameter validation, result processing
- **Integration**: Works with all tool types, monitoring system

#### `reasoning_engine.py`
- **Purpose**: Analyzes tasks and creates execution plans
- **Key Classes**: `ReasoningEngine`, `TaskAnalysis`, `ExecutionPlan`
- **Features**: Task decomposition, dependency analysis, resource planning
- **AI Integration**: Uses LLM for intelligent task understanding

#### `enhanced_workflow.py`
- **Purpose**: Hybrid workflow system with Temporal.io integration
- **Key Classes**: `EnhancedWorkflowEngine`, `EnhancedWorkflowRequest`
- **Features**: Intelligent engine selection, fallback mechanisms
- **Scalability**: Supports both simple and distributed workflows

### System Infrastructure
```
core/
├── config/
│   ├── config_manager.py           # Configuration management system
│   └── environments/               # Environment-specific configs
├── monitoring/
│   ├── metrics.py                  # Prometheus metrics collection
│   └── observability.py           # System observability tools
├── memory/
│   ├── memory_manager.py           # Memory system interface
│   └── memory_integration.py      # Memory system integration
└── database/
    └── database_manager.py         # Database abstraction layer
```

**Key Components:**

#### `config_manager.py`
- **Purpose**: Manages environment-specific configurations
- **Key Classes**: `ConfigManager`, `JarvisConfig`
- **Features**: Environment detection, variable substitution, validation
- **Security**: Secure secret management via environment variables

#### `metrics.py`
- **Purpose**: Comprehensive metrics collection for monitoring
- **Key Classes**: `JarvisMetrics`, `HealthChecker`
- **Features**: System metrics, workflow metrics, health monitoring
- **Integration**: Prometheus/Grafana stack integration

### Specialized Components
```
core/
├── llm/
│   ├── llm_manager.py              # Multi-provider LLM management
│   └── mock_client.py              # Testing mock client
├── voice/
│   ├── voice_interface.py          # TTS/STT integration
│   └── speech_cleaner.py           # Natural speech processing
├── email/
│   └── email_client.py             # IMAP/SMTP email client
├── automation/
│   └── web_automation.py           # Playwright web automation
└── execution/
    └── docker_executor.py          # Docker-based code execution
```

**Key Components:**

#### `llm_manager.py`
- **Purpose**: Manages multiple LLM providers with intelligent switching
- **Key Classes**: `LLMManager`, `LLMClient`, `LLMResponse`
- **Features**: Provider abstraction, failover, cost optimization
- **Providers**: Qwen, Claude, GPT, Gemini, Ollama support

#### `voice_interface.py`
- **Purpose**: Complete voice interaction system
- **Key Classes**: `VoiceInterface`, `TTSEngine`, `STTEngine`
- **Features**: Natural speech synthesis, speech recognition
- **Integration**: Works with speech cleaner for natural output

## 🔧 Tool System (`modules/tools/`)

### Tool Architecture
```
modules/tools/
├── base_tool.py                    # Base tool class & registry
├── calculator.py                   # Mathematical calculations
├── code_executor_tool.py           # Basic code execution
├── enhanced_code_executor_tool.py  # Docker-based code execution
├── email_tool.py                   # Email operations
├── file_manager.py                 # File system operations
├── human_input.py                  # Human interaction tool
├── terminal_executor.py            # Shell command execution
├── voice_tool.py                   # Voice interaction tool
├── web_browser_tool.py             # Web automation tool
└── web_search.py                   # Web search capabilities
```

**Key Components:**

#### `base_tool.py`
- **Purpose**: Foundation for all tools, provides registry system
- **Key Classes**: `BaseTool`, `ToolRegistry`, `ToolResult`
- **Features**: Tool validation, parameter mapping, result standardization
- **Pattern**: Template method pattern for consistent tool behavior

#### `enhanced_code_executor_tool.py`
- **Purpose**: Secure, Docker-based code execution
- **Key Classes**: `EnhancedCodeExecutorTool`
- **Features**: Multi-language support, sandboxing, security validation
- **Security**: Isolated execution environment, resource limits

#### `web_browser_tool.py`
- **Purpose**: Automated web interaction using Playwright
- **Key Classes**: `WebBrowserTool`
- **Features**: Page navigation, element interaction, screenshot capture
- **Capabilities**: JavaScript execution, form filling, data extraction

## ⚙️ Configuration System (`config/`)

### Configuration Structure
```
config/
├── environments/
│   ├── development.yaml            # Development environment settings
│   ├── production.yaml             # Production environment settings
│   └── testing.yaml                # Testing environment settings
└── init.sql                        # Database initialization
```

**Configuration Features:**
- **Environment Separation**: Different configs for dev/prod/test
- **Variable Substitution**: Environment variable integration
- **Validation**: Comprehensive configuration validation
- **Security**: Secrets management via environment variables

## 🔄 Workflow System (`workflows/` & `core/workflows/`)

### Workflow Components
```
workflows/
├── custom/                         # Custom workflow definitions
└── templates/                      # Workflow templates

core/workflows/
├── temporal_engine.py              # Temporal.io integration
└── jarvis_workflows.py             # Pre-built workflow patterns
```

**Key Components:**

#### `temporal_engine.py`
- **Purpose**: Enterprise-grade workflow management
- **Key Classes**: `TemporalWorkflowEngine`, `WorkflowRequest`
- **Features**: Distributed execution, fault tolerance, persistence
- **Integration**: Seamless integration with JARVIS tool system

#### `jarvis_workflows.py`
- **Purpose**: Pre-built workflow patterns for common tasks
- **Key Classes**: `SimpleTaskWorkflow`, `MultiStepTaskWorkflow`
- **Features**: Activity functions, LLM integration, approval workflows
- **Patterns**: Common workflow templates for rapid development

## 🎓 Skills Framework (`skills/`)

### Skills Architecture
```
skills/
└── skill_framework.py              # Skills system foundation
```

**Skills System:**
- **Base Classes**: Foundation for skill development
- **Skill Registry**: Dynamic skill loading and management
- **Learning Integration**: Feedback loops for skill improvement
- **Extensibility**: Plugin-based skill architecture

## 🧪 Testing System (`tests/` & test files)

### Test Structure
```
tests/
└── comprehensive_tests.py          # Main test suite

# Individual test files:
├── test_layer1.py                  # Foundation layer tests
├── test_layer2.py                  # Reasoning engine tests
├── test_layer3.py                  # Execution engine tests
├── test_temporal_integration.py    # Temporal.io tests
├── test_enhanced_code_execution.py # Code execution tests
└── test_*.py                       # Component-specific tests
```

**Testing Strategy:**
- **Layer Testing**: Each architectural layer tested independently
- **Integration Testing**: Cross-component interaction testing
- **Performance Testing**: Load and stress testing
- **Security Testing**: Vulnerability and penetration testing

## 📊 Monitoring System (`monitoring/`)

### Monitoring Stack
```
monitoring/
├── prometheus.yml                  # Prometheus configuration
├── alertmanager.yml               # Alert management rules
└── grafana/
    ├── provisioning/              # Auto-provisioning configs
    └── dashboards/                # Dashboard definitions
```

**Monitoring Features:**
- **Metrics Collection**: System and application metrics
- **Alerting**: Intelligent alert rules and notifications
- **Dashboards**: Real-time visualization and analysis
- **Health Monitoring**: Component health tracking

## 🚀 Application Entry Points

### Main Applications
```
├── main.py                         # Primary JARVIS application
├── config_cli.py                   # Configuration management CLI
├── temporal_cli.py                 # Workflow management CLI
├── email_cli.py                    # Email system CLI
├── voice_cli.py                    # Voice system CLI
└── llm_cli.py                      # LLM management CLI
```

**CLI Tools:**
- **Modular CLIs**: Specialized command-line interfaces
- **Testing Tools**: Individual component testing
- **Management Tools**: System administration utilities
- **Development Tools**: Development and debugging aids

## 🔧 Development Files

### Development Support
```
├── COMPLETION_ROADMAP.py           # Development progress tracking
├── PROGRESS_TRACKER.py             # Task completion monitoring
├── requirements_*.txt              # Dependency specifications
├── docker-compose-*.yml            # Container orchestration
└── setup_*.sh                      # Setup and installation scripts
```

## 📚 Documentation (`user_manual/`)

### Documentation Structure
```
user_manual/
├── README.md                       # Main documentation index
├── architecture/
│   └── system_architecture.md     # System design documentation
├── development/
│   └── directory_structure.md     # This file
├── monitoring/
│   ├── monitoring_guide.md        # Monitoring system guide
│   └── metrics_reference.md       # Metrics catalog
├── configuration/
│   └── config_guide.md            # Configuration management
└── troubleshooting/
    └── common_issues.md            # Problem resolution guide
```

## 🎯 Key Design Patterns

### 1. **Registry Pattern**
- **Used in**: Tool system, skill framework
- **Purpose**: Dynamic component registration and discovery
- **Benefits**: Extensibility, loose coupling

### 2. **Strategy Pattern**
- **Used in**: Workflow engines, LLM providers
- **Purpose**: Algorithm selection at runtime
- **Benefits**: Flexibility, maintainability

### 3. **Observer Pattern**
- **Used in**: Monitoring system, event handling
- **Purpose**: Decoupled event notification
- **Benefits**: Scalability, modularity

### 4. **Template Method Pattern**
- **Used in**: Base tool class, skill framework
- **Purpose**: Common algorithm structure with customization
- **Benefits**: Code reuse, consistency

## 🔄 Data Flow Architecture

### Request Processing Flow
1. **Input** → `main.py` → **Reasoning Engine**
2. **Reasoning Engine** → **Task Analysis** → **Execution Plan**
3. **Execution Plan** → **Workflow Engine** → **Tool Selection**
4. **Tool Execution** → **Result Processing** → **Response**
5. **Monitoring** → **Metrics Collection** → **Dashboard Updates**

### Configuration Flow
1. **Environment Detection** → **Config Loading** → **Validation**
2. **Variable Substitution** → **Object Creation** → **System Initialization**

### Monitoring Flow
1. **Metrics Collection** → **Prometheus** → **Grafana**
2. **Health Checks** → **Alertmanager** → **Notifications**

---

*This directory structure provides a complete foundation for understanding, maintaining, and extending JARVIS. Each component is designed for modularity, testability, and scalability.*
