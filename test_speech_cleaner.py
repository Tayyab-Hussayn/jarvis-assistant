#!/usr/bin/env python3
"""
Test Speech Cleaner
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.voice.speech_cleaner import speech_cleaner

def test_speech_cleaning():
    """Test speech text cleaning"""
    
    print("🧪 Testing Speech Text Cleaner")
    print("=" * 40)
    
    test_cases = [
        # Technical text with symbols
        'The function calculate_sum() returns a value.',
        'Check the API at https://api.example.com/v1/users',
        'Set the variable "user_name" to "John_Doe"',
        'The file path is /home/user/documents/file.txt',
        'Price: $29.99 (includes 15% tax)',
        'Email me at john@example.com for details',
        'The array [1, 2, 3] has {length: 3} items',
        'Use HTTP/HTTPS for secure connections',
        'The condition (x >= 10 && y <= 5) is true',
        'Version 2.1.0 includes bug fixes',
        
        # Code-like text
        'if (user != null) { return user.name; }',
        'SELECT * FROM users WHERE age > 18;',
        'const API_KEY = "abc123_def456";',
        
        # Mixed content
        'JARVIS can process JSON/XML data at 95% accuracy!'
    ]
    
    for i, original in enumerate(test_cases, 1):
        cleaned = speech_cleaner.clean_for_speech(original)
        
        print(f"\n{i}. Original:")
        print(f"   {original}")
        print(f"   Cleaned:")
        print(f"   {cleaned}")
    
    print(f"\n✅ Speech cleaning test complete!")
    print(f"JARVIS will now speak naturally without technical symbols!")

if __name__ == "__main__":
    test_speech_cleaning()
