#!/usr/bin/env python3
"""
Speech Text Cleaner - Clean text for natural speech
"""

import re

class SpeechTextCleaner:
    """Clean text to make it sound natural when spoken"""
    
    def __init__(self):
        # Define replacements for symbols
        self.symbol_replacements = {
            # Brackets and parentheses
            '(': ' ',
            ')': ' ',
            '[': ' ',
            ']': ' ',
            '{': ' ',
            '}': ' ',
            '<': ' ',
            '>': ' ',
            
            # Quotes
            '"': ' ',
            "'": ' ',
            '`': ' ',
            
            # Dashes and underscores
            '_': ' ',
            '--': ' ',
            '---': ' ',
            
            # Slashes and symbols
            '/': ' slash ',
            '\\': ' ',
            '|': ' ',
            
            # Colons and semicolons
            ':': ' ',
            ';': ' ',
            
            # Other symbols
            '*': ' ',
            '#': ' ',
            '@': ' at ',
            '&': ' and ',
            '%': ' percent ',
            '$': ' dollars ',
            '€': ' euros ',
            '£': ' pounds ',
            
            # Technical symbols
            '+=': ' plus equals ',
            '==': ' equals ',
            '!=': ' not equals ',
            '<=': ' less than or equal ',
            '>=': ' greater than or equal ',
            '++': ' plus plus ',
            '--': ' minus minus ',
        }
        
        # Words to replace for better speech
        self.word_replacements = {
            'API': 'A P I',
            'URL': 'U R L',
            'HTTP': 'H T T P',
            'HTTPS': 'H T T P S',
            'JSON': 'J S O N',
            'XML': 'X M L',
            'SQL': 'S Q L',
            'HTML': 'H T M L',
            'CSS': 'C S S',
            'JS': 'JavaScript',
            'AI': 'A I',
            'ML': 'M L',
            'UI': 'U I',
            'UX': 'U X',
        }
    
    def clean_for_speech(self, text: str) -> str:
        """Clean text to make it natural for speech"""
        
        if not text:
            return ""
        
        # Start with original text
        cleaned = text
        
        # Replace technical symbols first (longer patterns first)
        for symbol, replacement in sorted(self.symbol_replacements.items(), 
                                        key=lambda x: len(x[0]), reverse=True):
            cleaned = cleaned.replace(symbol, replacement)
        
        # Replace technical words
        for word, replacement in self.word_replacements.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(word) + r'\b'
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing spaces
        cleaned = cleaned.strip()
        
        # Handle numbers in a more natural way
        cleaned = self._clean_numbers(cleaned)
        
        # Handle URLs and emails
        cleaned = self._clean_urls_emails(cleaned)
        
        # Remove any remaining problematic characters
        cleaned = self._final_cleanup(cleaned)
        
        return cleaned
    
    def _clean_numbers(self, text: str) -> str:
        """Make numbers more natural for speech"""
        
        # Convert version numbers like "1.0.0" to "version 1 point 0 point 0"
        text = re.sub(r'\b(\d+)\.(\d+)\.(\d+)\b', r'version \1 point \2 point \3', text)
        
        # Convert decimals like "3.14" to "3 point 14"
        text = re.sub(r'\b(\d+)\.(\d+)\b', r'\1 point \2', text)
        
        # Convert percentages
        text = re.sub(r'(\d+)%', r'\1 percent', text)
        
        return text
    
    def _clean_urls_emails(self, text: str) -> str:
        """Handle URLs and emails"""
        
        # Replace common URL patterns
        text = re.sub(r'https?://[^\s]+', 'a web link', text)
        text = re.sub(r'www\.[^\s]+', 'a website', text)
        
        # Replace email patterns  
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'an email address', text)
        
        # Replace file paths
        text = re.sub(r'/[^\s]+\.[a-zA-Z]{2,4}', 'a file path', text)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup of remaining issues"""
        
        # Remove any remaining special characters that might cause issues
        problematic_chars = ['~', '^', '`', '§', '±', '÷', '×']
        for char in problematic_chars:
            text = text.replace(char, ' ')
        
        # Clean up multiple spaces again
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure sentences end properly
        text = re.sub(r'([.!?])\s*$', r'\1', text)
        
        return text.strip()

# Global speech cleaner instance
speech_cleaner = SpeechTextCleaner()
