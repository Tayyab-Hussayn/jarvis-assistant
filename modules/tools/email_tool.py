#!/usr/bin/env python3
"""
Email Tool - JARVIS tool for email operations
"""

import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from modules.tools.base_tool import BaseTool, ToolResult, ToolStatus, tool_registry
from core.email.email_client import EmailClient, EmailConfig, EmailAutomation
import asyncio

class EmailTool(BaseTool):
    """Tool for email operations"""
    
    def __init__(self):
        super().__init__(name="email")
        self.description = "Send emails, check inbox, monitor for new messages"
        self.client = None
        self.automation = None
    
    def validate_input(self, action: str, **kwargs) -> bool:
        """Validate email action parameters"""
        
        valid_actions = ["send", "check_inbox", "monitor", "setup"]
        
        if action not in valid_actions:
            self.logger.error(f"Invalid action: {action}. Valid: {valid_actions}")
            return False
        
        if action == "send":
            if not kwargs.get("to_email") or not kwargs.get("subject") or not kwargs.get("body"):
                self.logger.error("Send action requires 'to_email', 'subject', and 'body' parameters")
                return False
        
        if action == "setup":
            if not kwargs.get("username") or not kwargs.get("password"):
                self.logger.error("Setup action requires 'username' and 'password' parameters")
                return False
        
        return True
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """Execute email action"""
        
        try:
            if action == "setup":
                return await self._setup_email(kwargs)
            
            elif action == "send":
                return await self._send_email(kwargs)
            
            elif action == "check_inbox":
                return await self._check_inbox(kwargs)
            
            elif action == "monitor":
                return await self._start_monitoring(kwargs)
            
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
                error_message=f"Email error: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _setup_email(self, params: dict) -> ToolResult:
        """Setup email configuration"""
        try:
            config = EmailConfig(
                username=params["username"],
                password=params["password"],
                imap_server=params.get("imap_server", "imap.gmail.com"),
                smtp_server=params.get("smtp_server", "smtp.gmail.com")
            )
            
            self.client = EmailClient(config)
            self.automation = EmailAutomation(config)
            
            # Test connections
            imap_ok = await self.client.connect_imap()
            smtp_ok = await self.client.connect_smtp()
            
            if imap_ok and smtp_ok:
                return ToolResult(
                    success=True,
                    output={
                        "message": "Email client configured successfully",
                        "imap_connected": imap_ok,
                        "smtp_connected": smtp_ok
                    },
                    status=ToolStatus.SUCCESS
                )
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Failed to connect to email servers",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Email setup failed: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _send_email(self, params: dict) -> ToolResult:
        """Send email"""
        if not self.client:
            return ToolResult(
                success=False,
                output=None,
                error_message="Email client not configured. Use 'setup' action first.",
                status=ToolStatus.FAILURE
            )
        
        try:
            success = await self.client.send_email(
                to_email=params["to_email"],
                subject=params["subject"],
                body=params["body"],
                attachments=params.get("attachments", [])
            )
            
            if success:
                return ToolResult(
                    success=True,
                    output={
                        "message": f"Email sent to {params['to_email']}",
                        "subject": params["subject"]
                    },
                    status=ToolStatus.SUCCESS
                )
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Failed to send email",
                    status=ToolStatus.FAILURE
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Send email failed: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _check_inbox(self, params: dict) -> ToolResult:
        """Check inbox for new emails"""
        if not self.client:
            return ToolResult(
                success=False,
                output=None,
                error_message="Email client not configured. Use 'setup' action first.",
                status=ToolStatus.FAILURE
            )
        
        try:
            limit = params.get("limit", 5)
            emails = await self.client.get_unread_emails(limit=limit)
            
            email_summaries = []
            for email_msg in emails:
                email_summaries.append({
                    "from": email_msg.sender,
                    "subject": email_msg.subject,
                    "body_preview": email_msg.body[:100] + "..." if len(email_msg.body) > 100 else email_msg.body,
                    "timestamp": email_msg.timestamp.isoformat() if hasattr(email_msg.timestamp, 'isoformat') else str(email_msg.timestamp)
                })
            
            return ToolResult(
                success=True,
                output={
                    "unread_count": len(emails),
                    "emails": email_summaries
                },
                status=ToolStatus.SUCCESS
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error_message=f"Check inbox failed: {str(e)}",
                status=ToolStatus.FAILURE
            )
    
    async def _start_monitoring(self, params: dict) -> ToolResult:
        """Start email monitoring"""
        return ToolResult(
            success=True,
            output={
                "message": "Email monitoring available",
                "note": "Use email_automation.monitor_emails() for continuous monitoring"
            },
            status=ToolStatus.SUCCESS
        )

# Register the tool
tool_registry.register_tool(EmailTool())
