# JARVIS Examples Directory

This directory contains demonstration files, test suites, and example implementations for JARVIS AI Agent.

## 📁 **Directory Structure**

```
examples/
├── README.md           # This file - examples overview
├── demos/              # Feature demonstrations
│   ├── README.md       # Demo documentation
│   ├── demo_natural_speech.py    # Natural speech demo
│   └── jarvis_voice.py           # Voice interface demo
└── tests/              # Active test suites
    ├── README.md       # Test documentation
    ├── test_all_complex_problems.py      # Complex scenarios
    ├── test_enhanced_code_execution.py   # Performance testing
    └── test_temporal_integration.py      # Integration testing
```

## 🎭 **Demonstrations**

### **Voice System Demos**
- **Natural Speech**: Text cleaning for natural speech output
- **Voice Interface**: Interactive voice conversation with JARVIS

### **Usage**
```bash
cd examples/demos
python demo_natural_speech.py
python jarvis_voice.py
```

## 🧪 **Testing**

### **Integration Tests**
- **Complex Problems**: Multi-component problem-solving validation
- **Temporal Integration**: Workflow system testing

### **Performance Tests**
- **Enhanced Code Execution**: Docker-based execution testing

### **Usage**
```bash
cd examples/tests
python test_temporal_integration.py
python test_enhanced_code_execution.py
```

## 🎯 **Purpose**

### **For Users**
- **Learn JARVIS capabilities** through interactive demos
- **Understand features** with practical examples
- **Get started quickly** with working demonstrations

### **For Developers**
- **Validate system functionality** with comprehensive tests
- **Performance benchmarking** with execution tests
- **Integration verification** with workflow tests
- **Reference implementations** for new features

## 🚀 **Getting Started**

### **Prerequisites**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
python config_cli.py create-env
# Set LLM_API_KEY in .env file

# Start services (for tests)
docker-compose -f docker-compose-temporal.yml up -d
```

### **Quick Demo**
```bash
# Try the natural speech demo
cd examples/demos
python demo_natural_speech.py
```

### **Quick Test**
```bash
# Run integration test
cd examples/tests
python test_temporal_integration.py
```

## 📚 **Additional Resources**

- **User Manual**: `../user_manual/` - Complete system documentation
- **Archived Tests**: `../tests/archive/` - Historical test suite (15 files)
- **CLI Tools**: Root directory - Management and testing tools

**Status**: Ready for demonstrations and system validation 🎭🧪
