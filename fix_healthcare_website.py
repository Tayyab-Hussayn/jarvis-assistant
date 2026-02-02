#!/usr/bin/env python3
"""
Fix Healthcare Website - Apply content filter to clean up the file
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.content_filter import content_filter

def fix_healthcare_website():
    """Fix the healthcare website by applying content filter"""
    
    file_path = "/home/krawin/exp.code/jarvis/workspace/healthcare_website/index.html"
    
    print("🏥 Fixing Healthcare Website")
    print("=" * 40)
    
    # Read the problematic file
    with open(file_path, 'r') as f:
        messy_content = f.read()
    
    print(f"📝 Original file size: {len(messy_content)} characters")
    
    # Apply content filter
    clean_html = content_filter.extract_code(messy_content, 'html')
    
    print(f"✨ Clean file size: {len(clean_html)} characters")
    print(f"🎯 Reduction: {((len(messy_content) - len(clean_html)) / len(messy_content) * 100):.1f}%")
    
    # Write clean content back
    with open(file_path, 'w') as f:
        f.write(clean_html)
    
    print("✅ Healthcare website fixed!")
    print(f"📁 File: {file_path}")
    
    # Verify the fix
    if clean_html.strip().startswith('<!DOCTYPE html'):
        print("✅ File now starts with proper HTML doctype")
    else:
        print("❌ Something went wrong with the fix")
    
    # Check for conversational text
    conversational_indicators = ["I'll build", "Here's the", "This creates", "### Online Medical"]
    has_conversation = any(indicator in clean_html for indicator in conversational_indicators)
    
    if not has_conversation:
        print("✅ No conversational text remaining")
    else:
        print("❌ Still contains some conversational text")
    
    print("\n📄 First 200 characters of clean file:")
    print("-" * 40)
    print(clean_html[:200] + "..." if len(clean_html) > 200 else clean_html)

if __name__ == "__main__":
    fix_healthcare_website()
