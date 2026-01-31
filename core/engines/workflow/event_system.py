"""
Event System - Simple event bus for inter-component communication
"""

import asyncio
import json
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str

class SimpleEventBus:
    """Simple in-memory event bus"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.events: List[Event] = []
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event_type: str, data: Dict[str, Any], source: str = "unknown"):
        """Publish event"""
        event = Event(event_type, data, datetime.now(), source)
        self.events.append(event)
        
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    print(f"Event handler error: {e}")
    
    def get_recent_events(self, limit: int = 10) -> List[Event]:
        """Get recent events"""
        return self.events[-limit:]

# Global event bus
event_bus = SimpleEventBus()
