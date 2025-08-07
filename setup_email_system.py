#!/usr/bin/env python3
"""
Setup and Demo Script for Automated Email Outreach System

This script demonstrates the complete email outreach workflow:
1. Import contacts from scraper
2. Configure email settings
3. Test email functionality
4. Set up daily automation

Author: AI Assistant
"""

import json
import os
import sys
from email_outreach_system import EmailOutreachSystem
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_email_config():
    """Interactive setup of email configuration"""
    print("🚀 EMAIL OUTREACH SYSTEM SETUP")
    print("=" * 50)
    
    config_file = "email_config.json"
    
    if os.path.exists(config_file):
        print(f"✅ Configuration file '{config_file}' already exists.")
        response = input("Do you want to reconfigure? (y/n): ").lower()
        if response != 'y':
            return
    
    print("\n📧 Email Service Setup")
    print("Choose your email service:")
    print("1. Gmail SMTP (recommended for testing)")
    print("2. SendGrid API (recommended for production)")
    print("3. Mailgun API")
    
    choice = input("Enter choice (1-3): ").strip()
    
    config = {
        "daily_email_limit": 50,
        "rate_limit_seconds": 30,
        "retry_attempts": 3,
        "unsubscribe_link": "https://yourwebsite.com/unsubscribe"
    }
    
    if choice == "1":
        print("\n📮 Gmail SMTP Setup")
        print("Note: You'll need to use an App Password, not your regular Gmail password.")
        print("Generate one at: https://myaccount.google.com/apppasswords")
        
        config["email_service"] = "smtp"
        config["smtp_settings"] = {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "username": input("Gmail address: ").strip(),
            "password": input("Gmail App Password: ").strip()
        }
        config["sender_email"] = config["smtp_settings"]["username"]
        
    elif choice == "2":
        print("\n📨 SendGrid API Setup")
        print("Get your API key from: https://app.sendgrid.com/settings/api_keys")
        
        config["email_service"] = "sendgrid"
        config["sendgrid_api_key"] = input("SendGrid API Key: ").strip()
        config["sender_email"] = input("Sender email address: ").strip()
        
    elif choice == "3":
        print("\n📪 Mailgun API Setup")
        print("Get your API key from: https://app.mailgun.com/app/account/security/api_keys")
        
        config["email_service"] = "mailgun"
        config["mailgun_settings"] = {
            "api_key": input("Mailgun API Key: ").strip(),
            "domain": input("Mailgun Domain: ").strip()
        }
        config["sender_email"] = input("Sender email address: ").strip()
    
    # Company information
    print("\n🏢 Company Information")
    config["sender_name"] = input("Your name/title: ").strip()
    config["company_info"] = {
        "name": input("Company name: ").strip(),
        "website": input("Company website: ").strip(),
        "phone": input("Phone number: ").strip(),
        "address": input("Company address: ").strip()
    }
    
    # Save configuration
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_file}")

def demo_email_system():
    """Demonstrate the email outreach system"""
    print("\n🎯 EMAIL OUTREACH SYSTEM DEMO")
    print("=" * 50)
    
    # Initialize system
    try:
        outreach = EmailOutreachSystem()
        print("✅ Email outreach system initialized")
    except Exception as e:
        print(f"❌ Failed to initialize system: {e}")
        return
    
    # Import contacts from scraper
    print("\n📥 Importing contacts from scraper...")
    imported_count = outreach.import_contacts_from_scraper()
    print(f"✅ Imported {imported_count} contacts")
    
    # Generate report
    print("\n📊 Current System Status:")
    report = outreach.generate_report()
    print(f"  Total Contacts: {report['total_contacts']}")
    print(f"  Daily Limit: {report['daily_limit']}")
    print(f"  Remaining Today: {report['remaining_today']}")
    
    if report['status_breakdown']:
        print("  Status Breakdown:")
        for status, count in report['status_breakdown'].items():
            print(f"    {status}: {count}")
    
    # Test email (optional)
    if report['total_contacts'] > 0:
        test_email = input(f"\n📧 Send test email? Enter your email address (or press Enter to skip): ").strip()
        if test_email and '@' in test_email:
            print("Sending test email...")
            # Create a test contact
            from email_outreach_system import EmailContact
            import uuid
            
            test_contact = EmailContact(
                id=str(uuid.uuid4()),
                publication_name="Test Publication",
                email=test_email,
                website="https://test.com",
                category="magazine",
                description="Test publication for demo"
            )
            
            success = outreach.send_email(test_contact)
            if success:
                print("✅ Test email sent successfully!")
            else:
                print("❌ Failed to send test email. Check your configuration.")

def show_usage_examples():
    """Show usage examples for the email system"""
    print("\n📖 USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("Import contacts from scraper", 
         "python3 email_outreach_system.py --import-contacts"),
        
        ("Run immediate outreach campaign", 
         "python3 email_outreach_system.py --run-outreach"),
        
        ("Start daily scheduled outreach", 
         "python3 email_outreach_system.py --schedule"),
        
        ("Generate campaign report", 
         "python3 email_outreach_system.py --report"),
        
        ("Send limited number of emails", 
         "python3 email_outreach_system.py --run-outreach --max-emails 10"),
        
        ("Use custom config file", 
         "python3 email_outreach_system.py --config my_config.json --report")
    ]
    
    for description, command in examples:
        print(f"\n📋 {description}:")
        print(f"   {command}")

def create_cron_job():
    """Instructions for setting up cron job for daily automation"""
    print("\n⏰ DAILY AUTOMATION SETUP")
    print("=" * 50)
    
    print("To run 50 emails automatically every day at 9 AM, add this to your crontab:")
    print()
    print("1. Open crontab editor:")
    print("   crontab -e")
    print()
    print("2. Add this line:")
    current_dir = os.getcwd()
    print(f"   0 9 * * * cd {current_dir} && python3 email_outreach_system.py --run-outreach")
    print()
    print("3. Save and exit")
    print()
    print("Alternative: Use the built-in scheduler:")
    print("   python3 email_outreach_system.py --schedule")
    print("   (This runs continuously and handles scheduling internally)")

def main():
    """Main setup function"""
    print("🎯 PET INDUSTRY EMAIL OUTREACH SYSTEM")
    print("=" * 60)
    print("Automated daily email outreach to pet industry publications")
    print("=" * 60)
    
    while True:
        print("\nChoose an option:")
        print("1. 📧 Setup Email Configuration")
        print("2. 🎮 Demo Email System")
        print("3. 📖 Show Usage Examples")
        print("4. ⏰ Setup Daily Automation")
        print("5. 📊 Generate Report")
        print("6. 🚀 Start Daily Outreach Now")
        print("7. ❌ Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            setup_email_config()
        
        elif choice == "2":
            demo_email_system()
        
        elif choice == "3":
            show_usage_examples()
        
        elif choice == "4":
            create_cron_job()
        
        elif choice == "5":
            try:
                outreach = EmailOutreachSystem()
                report = outreach.generate_report()
                print("\n📊 CAMPAIGN REPORT")
                print("=" * 30)
                print(f"Total Contacts: {report['total_contacts']}")
                print(f"Emails Sent Today: {report['emails_sent_today']}")
                print(f"Emails This Week: {report['emails_sent_this_week']}")
                print(f"Daily Limit: {report['daily_limit']}")
                print(f"Remaining Today: {report['remaining_today']}")
                if report['status_breakdown']:
                    print("\nStatus Breakdown:")
                    for status, count in report['status_breakdown'].items():
                        print(f"  {status}: {count}")
            except Exception as e:
                print(f"❌ Error generating report: {e}")
        
        elif choice == "6":
            try:
                outreach = EmailOutreachSystem()
                print("🚀 Starting outreach campaign...")
                outreach.run_daily_outreach()
                print("✅ Outreach campaign completed!")
            except Exception as e:
                print(f"❌ Error running outreach: {e}")
        
        elif choice == "7":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()