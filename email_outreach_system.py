#!/usr/bin/env python3
"""
Automated Email Outreach System for Pet Industry Publications

This system integrates with the pet industry scraper to automatically
send personalized advertising outreach emails to publications daily.

Features:
- Multiple email API integrations (SendGrid, SMTP, etc.)
- Professional email templates
- Daily automation (50 emails/day)
- Contact management and tracking
- Rate limiting and spam prevention
- Analytics and reporting

Author: AI Assistant
"""

import smtplib
import json
import csv
import sqlite3
from datetime import datetime, timedelta
import time
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import random
from typing import List, Dict, Optional
import argparse
from dataclasses import dataclass, asdict
import os
from pathlib import Path
import uuid

# Third-party email APIs
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("SendGrid not installed. Install with: pip install sendgrid")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Requests not installed. Install with: pip install requests")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_outreach.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EmailContact:
    """Data class for email contacts"""
    id: str
    publication_name: str
    email: str
    website: str
    category: str
    description: str
    first_contacted: Optional[str] = None
    last_contacted: Optional[str] = None
    times_contacted: int = 0
    response_received: bool = False
    status: str = "pending"  # pending, sent, responded, bounced, unsubscribed
    notes: str = ""

@dataclass
class EmailCampaign:
    """Data class for email campaigns"""
    id: str
    name: str
    subject_template: str
    email_template: str
    created_date: str
    active: bool = True

class EmailOutreachSystem:
    """Main class for automated email outreach"""
    
    def __init__(self, config_file="email_config.json"):
        """Initialize the email outreach system"""
        self.config_file = config_file
        self.config = self._load_config()
        self.db_path = "email_outreach.db"
        self._init_database()
        
        # Email service setup
        self.email_service = None
        self._setup_email_service()
        
        # Rate limiting
        self.daily_limit = self.config.get('daily_email_limit', 50)
        self.emails_sent_today = 0
        self.last_reset_date = datetime.now().date()
        
        # Email templates
        self.templates = self._load_templates()

    def _load_config(self) -> Dict:
        """Load email configuration"""
        default_config = {
            "email_service": "smtp",  # smtp, sendgrid, mailgun
            "smtp_settings": {
                "host": "smtp.gmail.com",
                "port": 587,
                "use_tls": True,
                "username": "",
                "password": ""
            },
            "sendgrid_api_key": "",
            "mailgun_settings": {
                "api_key": "",
                "domain": ""
            },
            "sender_email": "",
            "sender_name": "Pet Industry Marketing",
            "daily_email_limit": 50,
            "rate_limit_seconds": 30,
            "retry_attempts": 3,
            "unsubscribe_link": "https://yourwebsite.com/unsubscribe",
            "company_info": {
                "name": "Your Company Name",
                "website": "https://yourwebsite.com",
                "phone": "Your Phone Number",
                "address": "Your Address"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.warning(f"Could not load config file: {e}. Using defaults.")
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file: {self.config_file}")
        
        return default_config

    def _setup_email_service(self):
        """Setup the email service based on configuration"""
        service = self.config.get('email_service', 'smtp').lower()
        
        if service == 'sendgrid' and SENDGRID_AVAILABLE:
            api_key = self.config.get('sendgrid_api_key')
            if api_key:
                self.email_service = sendgrid.SendGridAPIClient(api_key=api_key)
                logger.info("SendGrid email service initialized")
            else:
                logger.warning("SendGrid API key not provided. Falling back to SMTP.")
                self.email_service = "smtp"
        elif service == 'mailgun' and REQUESTS_AVAILABLE:
            api_key = self.config.get('mailgun_settings', {}).get('api_key')
            domain = self.config.get('mailgun_settings', {}).get('domain')
            if api_key and domain:
                self.email_service = "mailgun"
                logger.info("Mailgun email service configured")
            else:
                logger.warning("Mailgun settings incomplete. Falling back to SMTP.")
                self.email_service = "smtp"
        else:
            self.email_service = "smtp"
            logger.info("Using SMTP email service")

    def _init_database(self):
        """Initialize SQLite database for contact management"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                publication_name TEXT,
                email TEXT UNIQUE,
                website TEXT,
                category TEXT,
                description TEXT,
                first_contacted TEXT,
                last_contacted TEXT,
                times_contacted INTEGER DEFAULT 0,
                response_received BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'pending',
                notes TEXT
            )
        ''')
        
        # Email campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT,
                subject_template TEXT,
                email_template TEXT,
                created_date TEXT,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Email logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_logs (
                id TEXT PRIMARY KEY,
                contact_id TEXT,
                campaign_id TEXT,
                sent_date TEXT,
                status TEXT,
                error_message TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts (id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def _load_templates(self) -> Dict:
        """Load email templates"""
        templates = {
            "advertising_inquiry": {
                "subject": "Advertising Partnership Opportunity - {publication_name}",
                "body": """Dear {publication_name} Team,

I hope this email finds you well. My name is {sender_name} and I represent {company_name}, a company that specializes in high-quality pet industry products and services.

I've been following {publication_name} and am impressed by your coverage of the pet industry and the engaged audience you've built. Your content on {website} demonstrates a deep understanding of pet owners' needs and industry trends.

We're currently looking to partner with respected publications like yours to reach pet enthusiasts through targeted advertising campaigns. Our advertising partnership would include:

• Premium display advertising placements
• Sponsored content opportunities  
• Product review collaborations
• Newsletter sponsorship options
• Custom advertising packages tailored to your audience

We believe {publication_name} would be an excellent partner for our upcoming campaigns focusing on pet health, nutrition, and care products. Our advertising investments typically range from $500 to $5,000+ per month depending on the scope and duration of the partnership.

I'd love to discuss how we can work together to create value for your readers while supporting your publication's growth. Could we schedule a brief 15-minute call this week to explore partnership opportunities?

Please let me know your availability, and I'll be happy to send over our media kit and recent campaign examples.

Best regards,
{sender_name}
{company_name}
{phone}
{email}
{website}

P.S. If you're not the right person to discuss advertising partnerships, could you please direct me to the appropriate contact? I appreciate your time.

---
If you'd prefer not to receive these messages, please click here to unsubscribe: {unsubscribe_link}
"""
            },
            "follow_up": {
                "subject": "Re: Advertising Partnership Opportunity - {publication_name}",
                "body": """Hi there,

I wanted to follow up on my previous email regarding advertising partnership opportunities with {publication_name}.

I understand you're likely busy, but I believe there's a great opportunity for us to work together. Our pet industry advertising campaigns have helped publications like yours increase revenue while providing valuable content to their audiences.

Quick highlights of what we offer:
• Flexible advertising budgets ($500-$5,000+ monthly)
• High-quality, pet-focused content and products
• Professional creative assets and support
• Performance tracking and optimization

Would you have just 10 minutes for a quick call to discuss how we might collaborate?

Best regards,
{sender_name}
{company_name}
{phone}

---
Unsubscribe: {unsubscribe_link}
"""
            }
        }
        return templates

    def import_contacts_from_scraper(self, csv_file="pet_industry_media_contacts.csv"):
        """Import contacts from the scraper output"""
        if not os.path.exists(csv_file):
            logger.error(f"Scraper output file not found: {csv_file}")
            return 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        imported_count = 0
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    emails = row.get('Emails', '').split(';')
                    
                    for email in emails:
                        email = email.strip()
                        if email and '@' in email:
                            contact_id = str(uuid.uuid4())
                            
                            try:
                                cursor.execute('''
                                    INSERT OR IGNORE INTO contacts 
                                    (id, publication_name, email, website, category, description, status)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    contact_id,
                                    row.get('Publication Name', ''),
                                    email,
                                    row.get('Website', ''),
                                    row.get('Category', 'magazine'),
                                    row.get('Description', ''),
                                    'pending'
                                ))
                                
                                if cursor.rowcount > 0:
                                    imported_count += 1
                                    
                            except sqlite3.IntegrityError:
                                # Email already exists, skip
                                continue
            
            conn.commit()
            logger.info(f"Imported {imported_count} new contacts from scraper data")
            
        except Exception as e:
            logger.error(f"Error importing contacts: {e}")
        finally:
            conn.close()
        
        return imported_count

    def send_email_smtp(self, to_email: str, subject: str, body: str, attachments: List = None) -> bool:
        """Send email using SMTP"""
        try:
            smtp_config = self.config['smtp_settings']
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments if any
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
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            if smtp_config.get('use_tls', True):
                server.starttls()
            
            server.login(smtp_config['username'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_email_sendgrid(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SendGrid API"""
        try:
            from_email = Email(self.config['sender_email'], self.config['sender_name'])
            to_email_obj = To(to_email)
            content = Content("text/plain", body)
            
            mail = Mail(from_email, to_email_obj, subject, content)
            
            response = self.email_service.send(mail)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to_email} via SendGrid")
                return True
            else:
                logger.error(f"SendGrid error {response.status_code}: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid to {to_email}: {e}")
            return False

    def send_email_mailgun(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Mailgun API"""
        try:
            domain = self.config['mailgun_settings']['domain']
            api_key = self.config['mailgun_settings']['api_key']
            
            response = requests.post(
                f"https://api.mailgun.net/v3/{domain}/messages",
                auth=("api", api_key),
                data={
                    "from": f"{self.config['sender_name']} <{self.config['sender_email']}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": body
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully to {to_email} via Mailgun")
                return True
            else:
                logger.error(f"Mailgun error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email via Mailgun to {to_email}: {e}")
            return False

    def send_email(self, contact: EmailContact, campaign_id: str = "advertising_inquiry") -> bool:
        """Send email to a contact"""
        
        # Check daily limit
        if self._check_daily_limit():
            logger.warning("Daily email limit reached. Stopping for today.")
            return False
        
        # Get campaign template
        template_name = campaign_id
        if template_name not in self.templates:
            template_name = "advertising_inquiry"
        
        template = self.templates[template_name]
        
        # Format email content
        format_data = {
            'publication_name': contact.publication_name,
            'website': contact.website,
            'sender_name': self.config['sender_name'],
            'company_name': self.config['company_info']['name'],
            'phone': self.config['company_info']['phone'],
            'email': self.config['sender_email'],
            'company_website': self.config['company_info']['website'],
            'unsubscribe_link': self.config['unsubscribe_link']
        }
        
        subject = template['subject'].format(**format_data)
        body = template['body'].format(**format_data)
        
        # Send email based on configured service
        success = False
        
        if self.email_service == "sendgrid" and SENDGRID_AVAILABLE:
            success = self.send_email_sendgrid(contact.email, subject, body)
        elif self.email_service == "mailgun" and REQUESTS_AVAILABLE:
            success = self.send_email_mailgun(contact.email, subject, body)
        else:
            success = self.send_email_smtp(contact.email, subject, body)
        
        # Log the attempt
        self._log_email_attempt(contact.id, campaign_id, success)
        
        if success:
            self._update_contact_after_email(contact.id)
            self.emails_sent_today += 1
            
            # Rate limiting
            time.sleep(self.config.get('rate_limit_seconds', 30))
        
        return success

    def _check_daily_limit(self) -> bool:
        """Check if daily email limit is reached"""
        current_date = datetime.now().date()
        
        # Reset counter if it's a new day
        if current_date != self.last_reset_date:
            self.emails_sent_today = 0
            self.last_reset_date = current_date
        
        return self.emails_sent_today >= self.daily_limit

    def _log_email_attempt(self, contact_id: str, campaign_id: str, success: bool):
        """Log email attempt to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        log_id = str(uuid.uuid4())
        status = "sent" if success else "failed"
        
        cursor.execute('''
            INSERT INTO email_logs (id, contact_id, campaign_id, sent_date, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (log_id, contact_id, campaign_id, datetime.now().isoformat(), status))
        
        conn.commit()
        conn.close()

    def _update_contact_after_email(self, contact_id: str):
        """Update contact record after sending email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE contacts 
            SET last_contacted = ?, 
                times_contacted = times_contacted + 1,
                status = 'sent',
                first_contacted = COALESCE(first_contacted, ?)
            WHERE id = ?
        ''', (now, now, contact_id))
        
        conn.commit()
        conn.close()

    def get_pending_contacts(self, limit: int = 50) -> List[EmailContact]:
        """Get pending contacts for outreach"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM contacts 
            WHERE status = 'pending' OR 
                  (status = 'sent' AND 
                   times_contacted < 2 AND 
                   DATE(last_contacted) < DATE('now', '-7 days'))
            ORDER BY first_contacted ASC, times_contacted ASC
            LIMIT ?
        ''', (limit,))
        
        contacts = []
        for row in cursor.fetchall():
            contact = EmailContact(
                id=row[0],
                publication_name=row[1],
                email=row[2],
                website=row[3],
                category=row[4],
                description=row[5],
                first_contacted=row[6],
                last_contacted=row[7],
                times_contacted=row[8],
                response_received=bool(row[9]),
                status=row[10],
                notes=row[11]
            )
            contacts.append(contact)
        
        conn.close()
        return contacts

    def run_daily_outreach(self, max_emails: int = None):
        """Run daily email outreach campaign"""
        if max_emails is None:
            max_emails = self.daily_limit
        
        logger.info(f"Starting daily outreach campaign (max {max_emails} emails)")
        
        # Get pending contacts
        contacts = self.get_pending_contacts(max_emails)
        
        if not contacts:
            logger.info("No pending contacts found for outreach")
            return
        
        logger.info(f"Found {len(contacts)} contacts for outreach")
        
        sent_count = 0
        failed_count = 0
        
        for contact in contacts:
            if self._check_daily_limit():
                logger.info("Daily email limit reached. Stopping outreach.")
                break
            
            # Determine campaign type
            campaign_id = "follow_up" if contact.times_contacted > 0 else "advertising_inquiry"
            
            logger.info(f"Sending email to {contact.email} ({contact.publication_name})")
            
            if self.send_email(contact, campaign_id):
                sent_count += 1
            else:
                failed_count += 1
            
            # Random delay between emails
            time.sleep(random.uniform(30, 60))
        
        logger.info(f"Daily outreach completed. Sent: {sent_count}, Failed: {failed_count}")

    def generate_report(self) -> Dict:
        """Generate outreach campaign report"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total contacts
        cursor.execute("SELECT COUNT(*) FROM contacts")
        total_contacts = cursor.fetchone()[0]
        
        # Contacts by status
        cursor.execute("SELECT status, COUNT(*) FROM contacts GROUP BY status")
        status_counts = dict(cursor.fetchall())
        
        # Emails sent today
        today = datetime.now().date().isoformat()
        cursor.execute("SELECT COUNT(*) FROM email_logs WHERE DATE(sent_date) = ?", (today,))
        emails_today = cursor.fetchone()[0]
        
        # Emails sent this week
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM email_logs WHERE sent_date >= ?", (week_ago,))
        emails_this_week = cursor.fetchone()[0]
        
        conn.close()
        
        report = {
            'total_contacts': total_contacts,
            'status_breakdown': status_counts,
            'emails_sent_today': emails_today,
            'emails_sent_this_week': emails_this_week,
            'daily_limit': self.daily_limit,
            'remaining_today': max(0, self.daily_limit - self.emails_sent_today)
        }
        
        return report

    def schedule_daily_outreach(self):
        """Schedule daily outreach using the schedule library"""
        # Schedule daily outreach at 9 AM
        schedule.every().day.at("09:00").do(self.run_daily_outreach)
        
        logger.info("Daily outreach scheduled for 9:00 AM")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description='Automated Email Outreach System')
    parser.add_argument('--import-contacts', action='store_true', help='Import contacts from scraper')
    parser.add_argument('--run-outreach', action='store_true', help='Run outreach campaign now')
    parser.add_argument('--schedule', action='store_true', help='Start scheduled outreach')
    parser.add_argument('--report', action='store_true', help='Generate campaign report')
    parser.add_argument('--max-emails', type=int, help='Maximum emails to send')
    parser.add_argument('--config', default='email_config.json', help='Config file path')
    
    args = parser.parse_args()
    
    # Initialize system
    outreach = EmailOutreachSystem(args.config)
    
    if args.import_contacts:
        count = outreach.import_contacts_from_scraper()
        print(f"Imported {count} new contacts")
    
    if args.run_outreach:
        outreach.run_daily_outreach(args.max_emails)
    
    if args.schedule:
        print("Starting scheduled daily outreach...")
        outreach.schedule_daily_outreach()
    
    if args.report:
        report = outreach.generate_report()
        print("\n" + "="*50)
        print("EMAIL OUTREACH CAMPAIGN REPORT")
        print("="*50)
        print(f"Total Contacts: {report['total_contacts']}")
        print(f"Emails Sent Today: {report['emails_sent_today']}")
        print(f"Emails This Week: {report['emails_sent_this_week']}")
        print(f"Daily Limit: {report['daily_limit']}")
        print(f"Remaining Today: {report['remaining_today']}")
        print("\nStatus Breakdown:")
        for status, count in report['status_breakdown'].items():
            print(f"  {status}: {count}")

if __name__ == "__main__":
    main()