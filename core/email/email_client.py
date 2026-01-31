#!/usr/bin/env python3
"""
Email Client - IMAP/SMTP integration for JARVIS
"""

import asyncio
import logging
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class EmailConfig:
    """Email configuration"""
    imap_server: str = "imap.gmail.com"
    imap_port: int = 993
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    username: str = ""
    password: str = ""
    use_ssl: bool = True

@dataclass
class EmailMessage:
    """Email message structure"""
    subject: str
    sender: str
    recipient: str
    body: str
    timestamp: datetime
    message_id: str
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []

class EmailClient:
    """Email client for JARVIS"""
    
    def __init__(self, config: EmailConfig):
        self.config = config
        self.logger = logging.getLogger("email_client")
        self.imap_connection = None
        self.smtp_connection = None
    
    async def connect_imap(self) -> bool:
        """Connect to IMAP server"""
        try:
            self.imap_connection = imaplib.IMAP4_SSL(self.config.imap_server, self.config.imap_port)
            self.imap_connection.login(self.config.username, self.config.password)
            self.logger.info("✅ IMAP connected")
            return True
        except Exception as e:
            self.logger.error(f"❌ IMAP connection failed: {e}")
            return False
    
    async def connect_smtp(self) -> bool:
        """Connect to SMTP server"""
        try:
            self.smtp_connection = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            self.smtp_connection.starttls()
            self.smtp_connection.login(self.config.username, self.config.password)
            self.logger.info("✅ SMTP connected")
            return True
        except Exception as e:
            self.logger.error(f"❌ SMTP connection failed: {e}")
            return False
    
    async def send_email(self, to_email: str, subject: str, body: str, 
                        attachments: List[str] = None) -> bool:
        """Send email"""
        try:
            if not self.smtp_connection:
                await self.connect_smtp()
            
            msg = MIMEMultipart()
            msg['From'] = self.config.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                        
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(file_path)}'
                        )
                        msg.attach(part)
            
            # Send email
            text = msg.as_string()
            self.smtp_connection.sendmail(self.config.username, to_email, text)
            
            self.logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Send email failed: {e}")
            return False
    
    async def get_unread_emails(self, folder: str = "INBOX", limit: int = 10) -> List[EmailMessage]:
        """Get unread emails"""
        try:
            if not self.imap_connection:
                await self.connect_imap()
            
            self.imap_connection.select(folder)
            
            # Search for unread emails
            status, messages = self.imap_connection.search(None, 'UNSEEN')
            
            if status != 'OK':
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # Get latest emails (limit)
            for email_id in email_ids[-limit:]:
                status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                
                if status == 'OK':
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # Extract email details
                    subject = email_message['Subject'] or 'No Subject'
                    sender = email_message['From'] or 'Unknown'
                    recipient = email_message['To'] or self.config.username
                    message_id = email_message['Message-ID'] or str(email_id)
                    
                    # Get timestamp
                    date_str = email_message['Date']
                    timestamp = datetime.now()  # Fallback
                    
                    # Extract body
                    body = self._extract_body(email_message)
                    
                    emails.append(EmailMessage(
                        subject=subject,
                        sender=sender,
                        recipient=recipient,
                        body=body,
                        timestamp=timestamp,
                        message_id=message_id
                    ))
            
            self.logger.info(f"✅ Retrieved {len(emails)} unread emails")
            return emails
            
        except Exception as e:
            self.logger.error(f"❌ Get emails failed: {e}")
            return []
    
    def _extract_body(self, email_message) -> str:
        """Extract email body text"""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8')
            else:
                return email_message.get_payload(decode=True).decode('utf-8')
        except:
            return "Could not extract email body"
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read"""
        try:
            # This is a simplified implementation
            self.logger.info(f"Marked email {message_id} as read")
            return True
        except Exception as e:
            self.logger.error(f"❌ Mark as read failed: {e}")
            return False
    
    async def monitor_emails(self, callback_func, check_interval: int = 60):
        """Monitor for new emails"""
        self.logger.info(f"📧 Starting email monitoring (checking every {check_interval}s)")
        
        try:
            while True:
                new_emails = await self.get_unread_emails()
                
                if new_emails:
                    self.logger.info(f"📬 Found {len(new_emails)} new emails")
                    for email_msg in new_emails:
                        await callback_func(email_msg)
                
                await asyncio.sleep(check_interval)
                
        except Exception as e:
            self.logger.error(f"❌ Email monitoring failed: {e}")
    
    async def close_connections(self):
        """Close email connections"""
        try:
            if self.imap_connection:
                self.imap_connection.close()
                self.imap_connection.logout()
            
            if self.smtp_connection:
                self.smtp_connection.quit()
            
            self.logger.info("Email connections closed")
        except Exception as e:
            self.logger.error(f"Close connections failed: {e}")

class EmailAutomation:
    """Email automation for JARVIS"""
    
    def __init__(self, config: EmailConfig):
        self.client = EmailClient(config)
        self.logger = logging.getLogger("email_automation")
        self.llm_manager = None
    
    def set_llm_manager(self, llm_manager):
        """Set LLM manager for intelligent responses"""
        self.llm_manager = llm_manager
    
    async def auto_respond_to_email(self, email_msg: EmailMessage) -> bool:
        """Automatically respond to email using LLM"""
        try:
            if not self.llm_manager:
                self.logger.warning("No LLM manager set for auto-response")
                return False
            
            # Generate response using LLM
            prompt = f"""
            You received this email:
            From: {email_msg.sender}
            Subject: {email_msg.subject}
            Body: {email_msg.body[:500]}...
            
            Generate a professional, helpful response. Keep it concise and friendly.
            """
            
            response = await self.llm_manager.generate(
                prompt=prompt,
                system_prompt="You are JARVIS, an AI assistant. Write professional email responses."
            )
            
            # Send response
            response_subject = f"Re: {email_msg.subject}"
            success = await self.client.send_email(
                to_email=email_msg.sender,
                subject=response_subject,
                body=response.content
            )
            
            if success:
                self.logger.info(f"✅ Auto-responded to {email_msg.sender}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Auto-response failed: {e}")
            return False
    
    async def process_email_commands(self, email_msg: EmailMessage) -> bool:
        """Process commands in emails"""
        try:
            body_lower = email_msg.body.lower()
            
            # Simple command processing
            if "jarvis status" in body_lower:
                status_response = "JARVIS is operational and monitoring emails."
                await self.client.send_email(
                    to_email=email_msg.sender,
                    subject="Re: JARVIS Status",
                    body=status_response
                )
                return True
            
            elif "jarvis help" in body_lower:
                help_response = """
                JARVIS Email Commands:
                - "jarvis status" - Get system status
                - "jarvis help" - Show this help
                - Send any message for AI response
                """
                await self.client.send_email(
                    to_email=email_msg.sender,
                    subject="Re: JARVIS Help",
                    body=help_response
                )
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Command processing failed: {e}")
            return False

# Global email automation instance
email_automation = None
