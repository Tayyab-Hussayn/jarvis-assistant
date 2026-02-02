#!/usr/bin/env python3
"""
Test Smart LLM Wrapper Detection - Verify file generation detection works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.smart_llm_wrapper import SmartLLMWrapper

def test_file_generation_detection():
    """Test that the smart wrapper correctly detects file generation requests"""
    
    print("🔍 Testing File Generation Detection")
    print("=" * 50)
    
    wrapper = SmartLLMWrapper()
    
    # Test cases: (prompt, should_detect, expected_type)
    test_cases = [
        # Should detect
        ("Create a portfolio website", True, "html"),
        ("Generate a Python script for data processing", True, "python"),
        ("Build a JavaScript function for authentication", True, "javascript"),
        ("Make a JSON configuration file", True, "json"),
        ("Write a CSS file for styling", True, "css"),
        ("Create an HTML landing page", True, "html"),
        ("Generate hello_world.py", True, "python"),
        ("Build a website with modern design", True, "html"),
        
        # Should NOT detect
        ("What is the weather today?", False, "generic"),
        ("Explain how Python works", False, "generic"),
        ("Tell me a joke", False, "generic"),
        ("How are you doing?", False, "generic"),
        ("What time is it?", False, "generic"),
    ]
    
    correct_detections = 0
    total_tests = len(test_cases)
    
    for i, (prompt, should_detect, expected_type) in enumerate(test_cases, 1):
        detected = wrapper._is_file_generation_request(prompt)
        detected_type = wrapper._detect_file_type_from_prompt(prompt)
        
        print(f"\n🧪 Test {i}: '{prompt[:40]}{'...' if len(prompt) > 40 else ''}'")
        
        if detected == should_detect:
            print(f"   ✅ Detection correct: {detected}")
            correct_detections += 1
        else:
            print(f"   ❌ Detection wrong: expected {should_detect}, got {detected}")
        
        if should_detect:
            if detected_type == expected_type:
                print(f"   ✅ Type correct: {detected_type}")
            else:
                print(f"   ⚠️ Type detection: expected {expected_type}, got {detected_type}")
        else:
            print(f"   ℹ️ Type: {detected_type}")
    
    print("\n" + "=" * 50)
    accuracy = (correct_detections / total_tests) * 100
    print(f"🎯 Detection Accuracy: {correct_detections}/{total_tests} ({accuracy:.1f}%)")
    
    if accuracy >= 90:
        print("🎉 Excellent! Smart wrapper detection is working great!")
    elif accuracy >= 75:
        print("👍 Good! Smart wrapper detection is working well.")
    else:
        print("⚠️ Detection needs improvement.")
    
    return accuracy >= 75

if __name__ == "__main__":
    test_file_generation_detection()
