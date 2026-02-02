#!/usr/bin/env python3
"""
Test Content Filter - Verify code extraction works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.content_filter import content_filter

def test_html_extraction():
    """Test HTML code extraction"""
    
    # Simulate problematic LLM response with conversational text
    messy_response = """### Online Medical Clinic Booking System

I'll build a comprehensive medical booking system with patient registration, doctor scheduling, appointment management, and admin features. Here's the complete solution:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediBook - Online Medical Clinic</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background: #3498db; color: white; padding: 20px; text-align: center; }
        .content { max-width: 800px; margin: 0 auto; padding: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MediBook Clinic</h1>
        <p>Professional Healthcare Services</p>
    </div>
    <div class="content">
        <h2>Book Your Appointment</h2>
        <p>Schedule your medical consultation today.</p>
    </div>
</body>
</html>
```

This creates a clean, professional medical booking website with modern styling and responsive design."""
    
    print("🧪 Testing HTML Content Filter")
    print("=" * 50)
    
    # Extract clean code
    clean_html = content_filter.extract_code(messy_response, 'html')
    
    print("📝 Original Response Length:", len(messy_response))
    print("✨ Filtered Code Length:", len(clean_html))
    print("🎯 Reduction:", f"{((len(messy_response) - len(clean_html)) / len(messy_response) * 100):.1f}%")
    print()
    
    # Verify clean code starts correctly
    if clean_html.strip().startswith('<!DOCTYPE html'):
        print("✅ Clean HTML starts correctly")
    else:
        print("❌ HTML extraction failed")
        print("First 100 chars:", clean_html[:100])
    
    # Verify no conversational text
    conversational_indicators = ["I'll build", "Here's the", "This creates"]
    has_conversation = any(indicator in clean_html for indicator in conversational_indicators)
    
    if not has_conversation:
        print("✅ No conversational text found")
    else:
        print("❌ Still contains conversational text")
    
    print("\n📄 Clean HTML Output:")
    print("-" * 30)
    print(clean_html[:200] + "..." if len(clean_html) > 200 else clean_html)

def test_python_extraction():
    """Test Python code extraction"""
    
    messy_python = """I'll create a simple Python script for you:

```python
#!/usr/bin/env python3
def hello_world():
    print("Hello, World!")
    return "success"

if __name__ == "__main__":
    result = hello_world()
    print(f"Result: {result}")
```

This script demonstrates basic Python functionality with a function and main execution block."""
    
    print("\n🐍 Testing Python Content Filter")
    print("=" * 50)
    
    clean_python = content_filter.extract_code(messy_python, 'python')
    
    print("📝 Original Response Length:", len(messy_python))
    print("✨ Filtered Code Length:", len(clean_python))
    print("🎯 Reduction:", f"{((len(messy_python) - len(clean_python)) / len(messy_python) * 100):.1f}%")
    
    if clean_python.strip().startswith('#!/usr/bin/env python3'):
        print("✅ Clean Python starts correctly")
    else:
        print("❌ Python extraction failed")
        print("First 50 chars:", clean_python[:50])
    
    print("\n📄 Clean Python Output:")
    print("-" * 30)
    print(clean_python)

if __name__ == "__main__":
    test_html_extraction()
    test_python_extraction()
    print("\n🎉 Content filter tests completed!")
