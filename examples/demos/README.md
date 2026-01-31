# JARVIS Demonstration Files

This directory contains demonstration scripts showcasing JARVIS capabilities and features.

## 🎭 **Available Demos**

### **Voice System Demonstrations**

#### `demo_natural_speech.py`
- **Purpose**: Demonstrates natural speech text cleaning feature
- **Features**: Shows how technical text is converted to natural speech
- **Usage**: `python demo_natural_speech.py`
- **Requirements**: Voice system dependencies

#### `jarvis_voice.py`
- **Purpose**: Interactive voice interface demonstration
- **Features**: Voice conversation with JARVIS
- **Usage**: `python jarvis_voice.py`
- **Requirements**: Voice system + LLM integration

---

## 🚀 **Running Demos**

### **Prerequisites**
```bash
# Ensure voice dependencies are installed
pip install -r requirements.txt

# Set up environment
python config_cli.py create-env
# Configure LLM_API_KEY in .env file
```

### **Voice System Demo**
```bash
# Natural speech cleaning demo
cd examples/demos
python demo_natural_speech.py

# Interactive voice demo
python jarvis_voice.py
```

---

## 🎯 **Demo Categories**

### **✅ Current Demos**
- **Voice Processing**: Natural speech and voice interaction
- **Speech Cleaning**: Technical text to natural speech conversion

### **🔮 Future Demo Ideas**
- **Workflow Automation**: Temporal.io workflow demonstrations
- **Code Execution**: Multi-language code execution examples
- **Email Automation**: Email processing and responses
- **Web Automation**: Browser automation scenarios
- **LLM Integration**: Multi-provider AI model switching

---

## 📚 **Learning Path**

1. **Start with**: `demo_natural_speech.py` - Simple feature showcase
2. **Advanced**: `jarvis_voice.py` - Interactive voice conversation
3. **Next**: Explore other JARVIS features via CLI tools

---

## 🛠️ **For Developers**

### **Creating New Demos**
1. Focus on single feature demonstration
2. Include clear documentation and usage instructions
3. Handle errors gracefully with user-friendly messages
4. Keep demos simple and educational

### **Demo Template**
```python
#!/usr/bin/env python3
"""
JARVIS Demo: [Feature Name]
Demonstrates [specific capability]
"""

async def main():
    print("🎭 JARVIS [Feature] Demo")
    print("=" * 30)
    
    # Demo implementation
    
if __name__ == "__main__":
    asyncio.run(main())
```

**Status**: Ready for feature demonstrations and user education 🎭
