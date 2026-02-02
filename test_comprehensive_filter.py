#!/usr/bin/env python3
"""
Comprehensive Content Filter Test - Verify all code types work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.content_filter import content_filter

def test_all_code_types():
    """Test content filter with various code types"""
    
    test_cases = {
        'html': """I'll create a beautiful website for you:

```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello World</h1></body>
</html>
```

This creates a simple webpage with proper structure.""",
        
        'python': """Here's a Python script:

```python
def main():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    main()
```

This demonstrates basic Python functionality.""",
        
        'javascript': """I'll build a JavaScript function:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
    return true;
}

greet("World");
```

This creates an interactive greeting function.""",
        
        'css': """Here's some CSS styling:

```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

.header {
    background: #333;
    color: white;
}
```

This provides clean, modern styling.""",
        
        'json': """I'll create a JSON configuration:

```json
{
    "name": "test-app",
    "version": "1.0.0",
    "dependencies": {
        "express": "^4.18.0"
    }
}
```

This defines the application configuration."""
    }
    
    print("🧪 Comprehensive Content Filter Test")
    print("=" * 50)
    
    all_passed = True
    
    for code_type, messy_content in test_cases.items():
        print(f"\n🔍 Testing {code_type.upper()} extraction:")
        
        clean_code = content_filter.extract_code(messy_content, code_type)
        
        # Calculate reduction
        reduction = ((len(messy_content) - len(clean_code)) / len(messy_content) * 100)
        print(f"   📝 Original: {len(messy_content)} chars")
        print(f"   ✨ Clean: {len(clean_code)} chars")
        print(f"   🎯 Reduction: {reduction:.1f}%")
        
        # Check for conversational text
        conversational_indicators = ["I'll", "Here's", "This creates", "This demonstrates", "This provides", "This defines"]
        has_conversation = any(indicator in clean_code for indicator in conversational_indicators)
        
        if has_conversation:
            print(f"   ❌ Still contains conversational text")
            all_passed = False
        else:
            print(f"   ✅ Clean code only")
        
        # Check code starts correctly
        expected_starts = {
            'html': '<!DOCTYPE html',
            'python': 'def main',
            'javascript': 'function greet',
            'css': 'body {',
            'json': '{'
        }
        
        if clean_code.strip().startswith(expected_starts[code_type]):
            print(f"   ✅ Starts correctly with '{expected_starts[code_type]}'")
        else:
            print(f"   ❌ Doesn't start with expected '{expected_starts[code_type]}'")
            print(f"   📄 Actually starts with: '{clean_code[:30]}...'")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Content filter is working perfectly.")
        print("✅ JARVIS will now generate clean, professional code files.")
    else:
        print("❌ Some tests failed. Content filter needs adjustment.")
    
    return all_passed

if __name__ == "__main__":
    test_all_code_types()
