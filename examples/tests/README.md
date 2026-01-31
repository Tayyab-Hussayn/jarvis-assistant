# JARVIS Test Files

This directory contains active test files for system validation, integration testing, and performance evaluation.

## 🧪 **Available Tests**

### **Integration Tests**

#### `test_all_complex_problems.py`
- **Purpose**: Comprehensive test suite for complex problem-solving
- **Coverage**: Data analysis, algorithms, web scraping, ML scenarios
- **Size**: 7.2 KB
- **Status**: ❌ Needs debugging (currently failing)
- **Usage**: `python test_all_complex_problems.py`

#### `test_temporal_integration.py`
- **Purpose**: Temporal.io workflow system integration testing
- **Coverage**: Workflow creation, execution, monitoring
- **Size**: 13.8 KB
- **Status**: ⏱️ Long-running test (comprehensive)
- **Usage**: `python test_temporal_integration.py`

### **Performance Tests**

#### `test_enhanced_code_execution.py`
- **Purpose**: Enhanced code execution system testing
- **Coverage**: Docker integration, multi-language execution, security
- **Size**: 8.0 KB
- **Status**: ⏱️ Performance testing (timeout expected)
- **Usage**: `python test_enhanced_code_execution.py`

---

## 🚀 **Running Tests**

### **Prerequisites**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt

# Start required services
docker-compose -f docker-compose-temporal.yml up -d
docker-compose -f docker-compose-monitoring.yml up -d

# Configure environment
python config_cli.py create-env
```

### **Individual Test Execution**
```bash
cd examples/tests

# Quick integration test
python test_temporal_integration.py

# Performance testing (may take time)
python test_enhanced_code_execution.py

# Complex problems (needs debugging)
python test_all_complex_problems.py
```

---

## 📊 **Test Categories**

### **✅ Integration Tests**
- **Temporal Workflows**: Enterprise workflow system validation
- **Complex Problems**: Multi-component problem-solving scenarios

### **⚡ Performance Tests**
- **Code Execution**: Docker-based execution performance
- **System Load**: Resource usage and limits testing

### **🔧 System Tests**
- **End-to-End**: Complete system functionality validation
- **Component Integration**: Inter-component communication testing

---

## 🎯 **Test Status**

| Test File | Type | Status | Action Required |
|-----------|------|--------|-----------------|
| `test_temporal_integration.py` | Integration | ⏱️ Long-running | Monitor execution |
| `test_enhanced_code_execution.py` | Performance | ⏱️ Timeout expected | Performance analysis |
| `test_all_complex_problems.py` | Integration | ❌ Failing | Debug and fix |

---

## 🛠️ **For Developers**

### **Test Development Guidelines**
1. **Clear Purpose**: Each test should validate specific functionality
2. **Proper Cleanup**: Ensure resources are cleaned up after tests
3. **Error Handling**: Graceful handling of test failures
4. **Documentation**: Clear description of what is being tested

### **Adding New Tests**
1. Create focused test for specific component
2. Include setup and teardown procedures
3. Add to appropriate category (integration/performance/system)
4. Update this README with test description

### **Debugging Failed Tests**
```bash
# Check system status
python config_cli.py test

# Verify services
docker-compose -f docker-compose-temporal.yml ps
docker-compose -f docker-compose-monitoring.yml ps

# Check logs
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

---

## 📚 **Historical Tests**

Completed tests have been archived in `../tests/archive/` directory:
- Layer tests (1, 2, 3) - Architecture validation ✅
- Component tests - Individual component validation ✅
- Complex problem tests (1-4) - Scenario validation ✅

**Status**: Active testing for system validation and performance monitoring 🧪
