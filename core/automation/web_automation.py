#!/usr/bin/env python3
"""
Web Browser Automation - Playwright integration for JARVIS
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import json
import base64

@dataclass
class BrowserConfig:
    """Browser automation configuration"""
    headless: bool = True
    timeout: int = 30000
    viewport: Dict[str, int] = None
    user_agent: str = None
    
    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1920, "height": 1080}

@dataclass
class WebAction:
    """Web automation action"""
    action_type: str  # click, type, scroll, screenshot, etc.
    selector: Optional[str] = None
    text: Optional[str] = None
    options: Optional[Dict] = None

class WebAutomation:
    """Web browser automation using Playwright"""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self.logger = logging.getLogger("web_automation")
        
        self.playwright = None
        self.browser = None
        self.page = None
        
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.config.headless
            )
            
            # Create context with config
            context = await self.browser.new_context(
                viewport=self.config.viewport,
                user_agent=self.config.user_agent
            )
            
            # Create page
            self.page = await context.new_page()
            self.page.set_default_timeout(self.config.timeout)
            
            self.logger.info("✅ Browser automation initialized")
            return True
            
        except ImportError:
            self.logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install")
            return False
        except Exception as e:
            self.logger.error(f"❌ Browser initialization failed: {e}")
            return False
    
    async def navigate_to(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            await self.page.goto(url)
            self.logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
    
    async def take_screenshot(self, path: Optional[str] = None) -> str:
        """Take screenshot and return base64 or save to file"""
        try:
            if path:
                await self.page.screenshot(path=path)
                self.logger.info(f"Screenshot saved to: {path}")
                return path
            else:
                screenshot_bytes = await self.page.screenshot()
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode()
                self.logger.info("Screenshot captured as base64")
                return screenshot_b64
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return ""
    
    async def extract_text(self, selector: str = "body") -> str:
        """Extract text from page or element"""
        try:
            text = await self.page.text_content(selector)
            return text or ""
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            return ""
    
    async def click_element(self, selector: str) -> bool:
        """Click an element"""
        try:
            await self.page.click(selector)
            self.logger.info(f"Clicked: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            return False
    
    async def type_text(self, selector: str, text: str) -> bool:
        """Type text into an element"""
        try:
            await self.page.fill(selector, text)
            self.logger.info(f"Typed text into: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Type failed: {e}")
            return False
    
    async def wait_for_element(self, selector: str, timeout: int = None) -> bool:
        """Wait for element to appear"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout or self.config.timeout)
            return True
        except Exception as e:
            self.logger.error(f"Wait for element failed: {e}")
            return False
    
    async def scroll_page(self, direction: str = "down", amount: int = 500) -> bool:
        """Scroll the page"""
        try:
            if direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
            elif direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            self.logger.info(f"Scrolled {direction}")
            return True
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
            return False
    
    async def extract_links(self) -> List[Dict[str, str]]:
        """Extract all links from page"""
        try:
            links = await self.page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(link => ({
                        text: link.textContent.trim(),
                        href: link.href,
                        title: link.title || ''
                    }));
                }
            """)
            return links
        except Exception as e:
            self.logger.error(f"Link extraction failed: {e}")
            return []
    
    async def fill_form(self, form_data: Dict[str, str]) -> bool:
        """Fill form fields"""
        try:
            for selector, value in form_data.items():
                await self.page.fill(selector, value)
            
            self.logger.info("Form filled successfully")
            return True
        except Exception as e:
            self.logger.error(f"Form filling failed: {e}")
            return False
    
    async def execute_actions(self, actions: List[WebAction]) -> List[Any]:
        """Execute a sequence of web actions"""
        results = []
        
        for action in actions:
            try:
                if action.action_type == "navigate":
                    result = await self.navigate_to(action.text)
                
                elif action.action_type == "click":
                    result = await self.click_element(action.selector)
                
                elif action.action_type == "type":
                    result = await self.type_text(action.selector, action.text)
                
                elif action.action_type == "screenshot":
                    result = await self.take_screenshot(action.text)
                
                elif action.action_type == "extract_text":
                    result = await self.extract_text(action.selector or "body")
                
                elif action.action_type == "scroll":
                    direction = action.options.get("direction", "down") if action.options else "down"
                    amount = action.options.get("amount", 500) if action.options else 500
                    result = await self.scroll_page(direction, amount)
                
                elif action.action_type == "wait":
                    result = await self.wait_for_element(action.selector)
                
                else:
                    result = f"Unknown action: {action.action_type}"
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Action {action.action_type} failed: {e}")
                results.append(False)
        
        return results
    
    async def scrape_page_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, str]:
        """Scrape specific data from a page"""
        try:
            await self.navigate_to(url)
            
            data = {}
            for key, selector in selectors.items():
                try:
                    text = await self.extract_text(selector)
                    data[key] = text
                except:
                    data[key] = ""
            
            return data
        except Exception as e:
            self.logger.error(f"Page scraping failed: {e}")
            return {}
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Browser close failed: {e}")

# Global web automation instance
web_automation = WebAutomation()
