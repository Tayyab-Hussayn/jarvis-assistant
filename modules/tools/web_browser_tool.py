#!/usr/bin/env python3
"""
Web Browser Tool - JARVIS tool for web automation
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus, tool_registry
from core.automation.web_automation import WebAutomation, BrowserConfig, WebAction
import json
import asyncio

class WebBrowserTool(BaseTool):
    """Tool for web browser automation and scraping"""
    
    def __init__(self):
        super().__init__(name="web_browser")
        self.description = "Automate web browsers, scrape data, take screenshots"
        self.automation = WebAutomation()
        self.initialized = False
    
    def validate_input(self, action: str, **kwargs) -> bool:
        """Validate web browser action parameters"""
        
        valid_actions = [
            "navigate", "screenshot", "extract_text", "click", 
            "type", "scroll", "scrape", "extract_links", "fill_form"
        ]
        
        if action not in valid_actions:
            self.logger.error(f"Invalid action: {action}. Valid: {valid_actions}")
            return False
        
        if action == "navigate" and not kwargs.get("url"):
            self.logger.error("Navigate action requires 'url' parameter")
            return False
        
        if action in ["click", "type"] and not kwargs.get("selector"):
            self.logger.error(f"{action} action requires 'selector' parameter")
            return False
        
        if action == "type" and not kwargs.get("text"):
            self.logger.error("Type action requires 'text' parameter")
            return False
        
        return True
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Execute web browser action"""
        
        try:
            # Initialize browser if needed
            if not self.initialized:
                success = await self.automation.initialize()
                if not success:
                    return ToolResult(
                        success=False,
                        output=None,
                        error_message="Failed to initialize browser. Install: pip install playwright && playwright install",
                        status=ToolStatus.FAILURE
                    )
                self.initialized = True
            
            # Execute action
            if action == "navigate":
                result = await self.automation.navigate_to(kwargs["url"])
                return ToolResult(
                    success=result,
                    output=f"Navigated to {kwargs['url']}" if result else None,
                    error_message="Navigation failed" if not result else None,
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            elif action == "screenshot":
                path = kwargs.get("path")
                result = await self.automation.take_screenshot(path)
                return ToolResult(
                    success=bool(result),
                    output={"screenshot": result, "type": "file" if path else "base64"},
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            elif action == "extract_text":
                selector = kwargs.get("selector", "body")
                text = await self.automation.extract_text(selector)
                return ToolResult(
                    success=True,
                    output={"text": text, "selector": selector},
                    status=ToolStatus.SUCCESS
                )
            
            elif action == "click":
                result = await self.automation.click_element(kwargs["selector"])
                return ToolResult(
                    success=result,
                    output=f"Clicked {kwargs['selector']}" if result else None,
                    error_message="Click failed" if not result else None,
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            elif action == "type":
                result = await self.automation.type_text(kwargs["selector"], kwargs["text"])
                return ToolResult(
                    success=result,
                    output=f"Typed text into {kwargs['selector']}" if result else None,
                    error_message="Type failed" if not result else None,
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            elif action == "scroll":
                direction = kwargs.get("direction", "down")
                amount = kwargs.get("amount", 500)
                result = await self.automation.scroll_page(direction, amount)
                return ToolResult(
                    success=result,
                    output=f"Scrolled {direction}" if result else None,
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            elif action == "extract_links":
                links = await self.automation.extract_links()
                return ToolResult(
                    success=True,
                    output={"links": links, "count": len(links)},
                    status=ToolStatus.SUCCESS
                )
            
            elif action == "scrape":
                url = kwargs.get("url")
                selectors = kwargs.get("selectors", {})
                
                if url:
                    data = await self.automation.scrape_page_data(url, selectors)
                else:
                    # Scrape current page
                    data = {}
                    for key, selector in selectors.items():
                        text = await self.automation.extract_text(selector)
                        data[key] = text
                
                return ToolResult(
                    success=True,
                    output={"scraped_data": data},
                    status=ToolStatus.SUCCESS
                )
            
            elif action == "fill_form":
                form_data = kwargs.get("form_data", {})
                result = await self.automation.fill_form(form_data)
                return ToolResult(
                    success=result,
                    output="Form filled successfully" if result else None,
                    error_message="Form filling failed" if not result else None,
                    status=ToolStatus.SUCCESS if result else ToolStatus.FAILURE
                )
            
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message=f"Unknown action: {action}",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Web browser error: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def close(self):
        """Close browser"""
        if self.initialized:
            await self.automation.close()
            self.initialized = False

# Register the tool
tool_registry.register_tool(WebBrowserTool())
