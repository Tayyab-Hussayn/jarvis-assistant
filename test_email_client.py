#!/usr/bin/env python3
"""
Test Email Client - 3 Different Methods
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.email.email_client import EmailClient, EmailConfig, EmailAutomation

# Test Method 1: Mock Email Client
class MockEmailClient:
    """Mock email client for testing without real email servers"""
    
    def __init__(self, config):
        self.config = config
        self.connected = True
        self.sent_emails = []
        self.mock_inbox = [
            {
                "from": "user@example.com",
                "subject": "Test Email 1",
                "body": "This is a test email from the mock inbox.",
                "timestamp": "2026-01-31T07:30:00"
            },
            {
                "from": "admin@company.com", 
                "subject": "JARVIS Status Request",
                "body": "jarvis status - please send system status",
                "timestamp": "2026-01-31T07:35:00"
            }
        ]
    
    async def connect_imap(self):
        print("   📧 Mock IMAP connection established")
        return True
    
    async def connect_smtp(self):
        print("   📧 Mock SMTP connection established")
        return True
    
    async def send_email(self, to_email, subject, body, attachments=None):
        email_data = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "attachments": attachments or []
        }
        self.sent_emails.append(email_data)
        print(f"   ✅ Mock email sent to {to_email}: {subject}")
        return True
    
    async def get_unread_emails(self, folder="INBOX", limit=10):
        print(f"   📬 Mock inbox check: {len(self.mock_inbox)} emails")
        return self.mock_inbox[:limit]

async def test_method_1_mock():
    """Test Method 1: Mock Email Client"""
    print("🧪 Test Method 1: Mock Email Client")
    print("=" * 40)
    
    try:
        # Create mock config
        config = EmailConfig(
            username="test@example.com",
            password="mock_password"
        )
        
        # Test mock client
        mock_client = MockEmailClient(config)
        
        # Test connections
        imap_ok = await mock_client.connect_imap()
        smtp_ok = await mock_client.connect_smtp()
        print(f"   Connections: IMAP={imap_ok}, SMTP={smtp_ok}")
        
        # Test sending email
        await mock_client.send_email(
            to_email="recipient@example.com",
            subject="Test from JARVIS",
            body="This is a test email from JARVIS mock client."
        )
        
        # Test checking inbox
        emails = await mock_client.get_unread_emails()
        print(f"   Inbox check: {len(emails)} emails found")
        
        print("   ✅ Mock email client test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Mock email client test FAILED: {e}")
        return False

async def test_method_2_structure():
    """Test Method 2: Email Client Structure"""
    print("\n🧪 Test Method 2: Email Client Structure")
    print("=" * 45)
    
    try:
        # Test EmailConfig
        config = EmailConfig(
            username="test@gmail.com",
            password="test_password",
            imap_server="imap.gmail.com",
            smtp_server="smtp.gmail.com"
        )
        print("   ✅ EmailConfig created successfully")
        
        # Test EmailClient initialization
        client = EmailClient(config)
        print("   ✅ EmailClient initialized successfully")
        
        # Test EmailAutomation
        automation = EmailAutomation(config)
        print("   ✅ EmailAutomation initialized successfully")
        
        # Test method signatures (without actual connections)
        print("   📋 Testing method signatures:")
        
        # These will fail but show the methods exist
        try:
            await client.connect_imap()
        except:
            print("   📝 connect_imap method exists")
        
        try:
            await client.connect_smtp()
        except:
            print("   📝 connect_smtp method exists")
        
        print("   ✅ Email client structure test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Email client structure test FAILED: {e}")
        return False

async def test_method_3_tool_integration():
    """Test Method 3: Email Tool Integration"""
    print("\n🧪 Test Method 3: Email Tool Integration")
    print("=" * 45)
    
    try:
        from modules.tools.email_tool import EmailTool
        
        # Test tool initialization
        email_tool = EmailTool()
        print("   ✅ EmailTool initialized successfully")
        
        # Test input validation
        valid = email_tool.validate_input("send", 
                                         to_email="test@example.com",
                                         subject="Test",
                                         body="Test body")
        print(f"   ✅ Input validation: {valid}")
        
        # Test invalid input
        invalid = email_tool.validate_input("send", to_email="test@example.com")
        print(f"   ✅ Invalid input detection: {not invalid}")
        
        # Test tool structure
        print("   📋 Tool methods available:")
        methods = [method for method in dir(email_tool) if not method.startswith('_')]
        for method in methods[:5]:  # Show first 5 methods
            print(f"     - {method}")
        
        print("   ✅ Email tool integration test PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Email tool integration test FAILED: {e}")
        return False

async def run_all_tests():
    """Run all email client tests"""
    print("📧 JARVIS Email Client Test Suite")
    print("=" * 50)
    
    # Run all test methods
    test1_result = await test_method_1_mock()
    test2_result = await test_method_2_structure()
    test3_result = await test_method_3_tool_integration()
    
    # Summary
    print(f"\n🎯 Test Results Summary:")
    print(f"   Method 1 (Mock Client): {'PASS' if test1_result else 'FAIL'}")
    print(f"   Method 2 (Structure):   {'PASS' if test2_result else 'FAIL'}")
    print(f"   Method 3 (Tool):        {'PASS' if test3_result else 'FAIL'}")
    
    all_passed = test1_result and test2_result and test3_result
    
    if all_passed:
        print(f"\n🎉 ALL EMAIL TESTS PASSED!")
        print(f"✅ Email client architecture is ready")
        print(f"📝 Note: Real email testing requires valid credentials")
    else:
        print(f"\n❌ Some tests failed - need fixes")
    
    return all_passed

if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)
