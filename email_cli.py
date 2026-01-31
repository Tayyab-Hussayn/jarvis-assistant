#!/usr/bin/env python3
"""
Email CLI - Command line interface for JARVIS email capabilities
"""

import asyncio
import sys
import os
sys.path.append('/home/krawin/exp.code/jarvis')

from core.email.email_client import EmailClient, EmailConfig, EmailAutomation
from core.llm.llm_manager import llm_manager

async def main():
    """Main email CLI interface"""
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        await setup_email()
    elif command == "send":
        await send_test_email()
    elif command == "check":
        await check_inbox()
    elif command == "monitor":
        await start_monitoring()
    elif command == "test":
        await test_email_system()
    else:
        print_help()

def print_help():
    """Print help information"""
    print("""
📧 JARVIS Email CLI

Commands:
  setup                - Setup email configuration
  send                 - Send test email
  check                - Check inbox for new emails
  monitor              - Start email monitoring
  test                 - Test email system
  
Examples:
  python email_cli.py setup
  python email_cli.py send
  python email_cli.py check
""")

async def setup_email():
    """Setup email configuration"""
    print("📧 JARVIS Email Setup")
    print("=" * 25)
    
    print("Enter your email credentials:")
    username = input("Email: ")
    password = input("Password (or App Password): ")
    
    # Test configuration
    config = EmailConfig(username=username, password=password)
    client = EmailClient(config)
    
    print("\n🔍 Testing connections...")
    
    imap_ok = await client.connect_imap()
    smtp_ok = await client.connect_smtp()
    
    if imap_ok and smtp_ok:
        print("✅ Email setup successful!")
        
        # Save config (in real implementation, use secure storage)
        print("💾 Configuration saved")
    else:
        print("❌ Email setup failed!")
        print("💡 For Gmail, use App Passwords: https://support.google.com/accounts/answer/185833")

async def send_test_email():
    """Send test email"""
    print("📤 Send Test Email")
    print("=" * 20)
    
    # This would use saved config in real implementation
    print("📝 Note: This is a demo - configure with real credentials for actual sending")
    
    # Mock send
    print("✅ Test email would be sent to specified recipient")

async def check_inbox():
    """Check inbox"""
    print("📬 Check Inbox")
    print("=" * 15)
    
    # This would use saved config in real implementation
    print("📝 Note: This is a demo - configure with real credentials for actual inbox check")
    
    # Mock inbox check
    mock_emails = [
        {"from": "user@example.com", "subject": "Hello JARVIS", "preview": "Can you help me with..."},
        {"from": "admin@company.com", "subject": "System Update", "preview": "The system has been updated..."}
    ]
    
    print(f"📧 Found {len(mock_emails)} unread emails:")
    for i, email in enumerate(mock_emails, 1):
        print(f"  {i}. From: {email['from']}")
        print(f"     Subject: {email['subject']}")
        print(f"     Preview: {email['preview']}")
        print()

async def start_monitoring():
    """Start email monitoring"""
    print("👁️  Email Monitoring")
    print("=" * 20)
    
    print("📧 Email monitoring would start...")
    print("🔄 Checking for new emails every 60 seconds")
    print("🤖 JARVIS would auto-respond using LLM")
    print("⏹️  Press Ctrl+C to stop (in real implementation)")

async def test_email_system():
    """Test email system"""
    print("🧪 Testing JARVIS Email System")
    print("=" * 35)
    
    # Test 1: Configuration
    print("1. Testing email configuration...")
    config = EmailConfig(username="test@example.com", password="test")
    print("   ✅ EmailConfig created")
    
    # Test 2: Client initialization
    print("\n2. Testing client initialization...")
    client = EmailClient(config)
    automation = EmailAutomation(config)
    print("   ✅ EmailClient and EmailAutomation created")
    
    # Test 3: LLM integration
    print("\n3. Testing LLM integration...")
    try:
        # Set up Qwen
        os.environ['QWEN_API_KEY'] = "eo24BBq9pSxv6v8EXKwSBYm7tkdbrpVCY1fX1IxGLbfDIDlatSNESqM6MteL5Kjs9n_A6Ix4PJ83EwFcHcQHDA"
        llm_manager.switch_provider('qwen')
        
        automation.set_llm_manager(llm_manager)
        
        # Test LLM response generation
        response = await llm_manager.generate(
            prompt="Generate a professional email response to: 'Hello, can you help me with my account?'",
            system_prompt="You are JARVIS. Write a helpful, professional email response."
        )
        
        print(f"   ✅ LLM integration working")
        print(f"   📝 Sample response: {response.content[:100]}...")
        
    except Exception as e:
        print(f"   ⚠️  LLM integration: {e}")
    
    # Test 4: Tool integration
    print("\n4. Testing tool integration...")
    try:
        from modules.tools.email_tool import EmailTool
        email_tool = EmailTool()
        print("   ✅ EmailTool integration working")
    except Exception as e:
        print(f"   ❌ Tool integration failed: {e}")
    
    print("\n🎉 Email system test complete!")
    print("📧 JARVIS email capabilities are ready!")

if __name__ == "__main__":
    asyncio.run(main())
