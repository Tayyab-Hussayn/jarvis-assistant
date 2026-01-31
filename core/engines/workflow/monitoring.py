"""
Monitoring System - File and email monitoring
"""

import asyncio
import os
from pathlib import Path
from typing import Callable, List
from datetime import datetime

class SimpleMonitor:
    """Simple file and system monitoring"""
    
    def __init__(self):
        self.file_watchers: List[Callable] = []
        self.running = False
    
    def add_file_watcher(self, path: str, callback: Callable):
        """Add file watcher"""
        self.file_watchers.append((path, callback))
    
    async def start_monitoring(self):
        """Start monitoring"""
        self.running = True
        while self.running:
            # Simple file monitoring - check if files exist
            for path, callback in self.file_watchers:
                if os.path.exists(path):
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(path)
                        else:
                            callback(path)
                    except Exception as e:
                        print(f"Monitor callback error: {e}")
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False

class SimpleEmailMonitor:
    """Simple email monitoring simulation"""
    
    def __init__(self):
        self.callbacks: List[Callable] = []
    
    def add_email_callback(self, callback: Callable):
        """Add email callback"""
        self.callbacks.append(callback)
    
    async def simulate_email(self, subject: str, body: str):
        """Simulate receiving an email"""
        email_data = {
            "subject": subject,
            "body": body,
            "timestamp": datetime.now().isoformat()
        }
        
        for callback in self.callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(email_data)
                else:
                    callback(email_data)
            except Exception as e:
                print(f"Email callback error: {e}")

# Global monitors
file_monitor = SimpleMonitor()
email_monitor = SimpleEmailMonitor()
