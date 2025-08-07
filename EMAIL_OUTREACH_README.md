# 📧 Automated Email Outreach System

**Complete automation for pet industry advertising outreach - Send 50 professional emails daily to publications**

## 🎯 System Overview

This automated email outreach system integrates seamlessly with the pet industry scraper to send professional advertising partnership emails to magazines, newspapers, and digital publications. The system handles everything from contact management to daily automation.

### ✨ Key Features

- **🔄 Full Automation**: Send 50 emails daily automatically
- **📊 Contact Management**: SQLite database tracks all interactions
- **📧 Multiple Email APIs**: Gmail SMTP, SendGrid, Mailgun support
- **🎨 Professional Templates**: Pre-written advertising outreach emails
- **⚡ Rate Limiting**: Prevents spam detection with intelligent delays
- **📈 Analytics**: Track sent emails, responses, and campaign performance
- **🔁 Follow-up System**: Automatic follow-up emails after 7 days
- **🛡️ Compliance**: Built-in unsubscribe links and CAN-SPAM compliance

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install --break-system-packages schedule sendgrid
```

### 2. Run Interactive Setup
```bash
python3 setup_email_system.py
```

### 3. Import Contacts from Scraper
```bash
python3 email_outreach_system.py --import-contacts
```

### 4. Start Daily Automation
```bash
python3 email_outreach_system.py --schedule
```

## 📋 Complete Workflow

### Step 1: Scrape Pet Industry Publications
```bash
# Run the scraper to find publications
python3 outreachscraper.py --max-sites 100 --output csv

# Results: pet_industry_media_contacts.csv with contact information
```

### Step 2: Import Contacts
```bash
# Import scraped contacts into email system
python3 email_outreach_system.py --import-contacts

# Result: 8 contacts imported from scraper data
```

### Step 3: Configure Email Service
Choose your preferred email service:

#### Option A: Gmail SMTP (Easy Setup)
```json
{
  "email_service": "smtp",
  "smtp_settings": {
    "host": "smtp.gmail.com",
    "port": 587,
    "use_tls": true,
    "username": "your-email@gmail.com",
    "password": "your-app-password"
  }
}
```

#### Option B: SendGrid API (Production Ready)
```json
{
  "email_service": "sendgrid",
  "sendgrid_api_key": "SG.your-api-key-here"
}
```

#### Option C: Mailgun API (Alternative)
```json
{
  "email_service": "mailgun",
  "mailgun_settings": {
    "api_key": "your-mailgun-api-key",
    "domain": "your-domain.com"
  }
}
```

### Step 4: Start Automated Outreach
```bash
# Option 1: Run once immediately
python3 email_outreach_system.py --run-outreach

# Option 2: Start daily scheduler
python3 email_outreach_system.py --schedule

# Option 3: Set up cron job for 9 AM daily
crontab -e
# Add: 0 9 * * * cd /workspace && python3 email_outreach_system.py --run-outreach
```

## 📧 Email Templates

### Initial Outreach Email
**Subject**: "Advertising Partnership Opportunity - [Publication Name]"

Professional email highlighting:
- Your company and pet industry focus
- Advertising partnership benefits
- Budget ranges ($500-$5,000+ monthly)
- Request for 15-minute call
- Media kit offer

### Follow-up Email
**Subject**: "Re: Advertising Partnership Opportunity - [Publication Name]"

Concise follow-up with:
- Quick partnership highlights
- Flexible budget options
- Request for 10-minute call
- Professional contact information

## 🎛️ Command Line Usage

### Core Commands
```bash
# Import contacts from scraper
python3 email_outreach_system.py --import-contacts

# Run outreach campaign now
python3 email_outreach_system.py --run-outreach

# Start daily scheduled outreach
python3 email_outreach_system.py --schedule

# Generate campaign report
python3 email_outreach_system.py --report

# Send limited number of emails
python3 email_outreach_system.py --run-outreach --max-emails 10

# Use custom config file
python3 email_outreach_system.py --config my_config.json --report
```

### Interactive Setup
```bash
# Full interactive setup
python3 setup_email_system.py

# Menu options:
# 1. Setup Email Configuration
# 2. Demo Email System  
# 3. Show Usage Examples
# 4. Setup Daily Automation
# 5. Generate Report
# 6. Start Daily Outreach Now
# 7. Exit
```

## 📊 Monitoring & Analytics

### Daily Reports
```bash
python3 email_outreach_system.py --report
```

**Sample Output:**
```
==================================================
EMAIL OUTREACH CAMPAIGN REPORT
==================================================
Total Contacts: 8
Emails Sent Today: 0
Emails This Week: 0
Daily Limit: 50
Remaining Today: 50

Status Breakdown:
  pending: 8
```

### Database Tables
The system maintains three SQLite tables:

1. **contacts** - Publication contact information
2. **campaigns** - Email campaign templates
3. **email_logs** - Detailed send history and tracking

## ⚙️ Configuration Options

### Email Settings
```json
{
  "daily_email_limit": 50,
  "rate_limit_seconds": 30,
  "retry_attempts": 3,
  "unsubscribe_link": "https://yourwebsite.com/unsubscribe"
}
```

### Company Information
```json
{
  "sender_name": "Pet Industry Marketing Team",
  "company_info": {
    "name": "Your Pet Company",
    "website": "https://yourpetcompany.com", 
    "phone": "(555) 123-4567",
    "address": "123 Pet Street, Pet City, PC 12345"
  }
}
```

## 🛡️ Safety & Compliance

### Anti-Spam Features
- **Rate Limiting**: 30-60 second delays between emails
- **Daily Limits**: Maximum 50 emails per day
- **Follow-up Logic**: Only 2 emails maximum per contact
- **Unsubscribe Links**: Every email includes unsubscribe option
- **CAN-SPAM Compliance**: Professional sender information

### Email Deliverability
- **Professional Templates**: Avoid spam trigger words
- **Gradual Ramp-up**: Start with smaller daily limits
- **Sender Reputation**: Use established email domains
- **Authentication**: Proper SPF, DKIM, DMARC setup

## 📈 Expected Results

### Contact Sources Found
From our test scraper run:
1. **The Denver Post** (Colorado) - 4 emails, 4 phone numbers
2. **Hi Animals Blog** - Pet care blog with contact email
3. **MN Pets** (Minnesota) - 2 phone numbers for pet services
4. **Kentucky Week for the Animals** - 5 contact numbers
5. **Animal Emergency Center** (Tennessee) - Veterinary hospital
6. **Montana Pets** - Regional pet publication
7. **Philadelphia Times** - Domain contact information

### Campaign Performance
- **Daily Output**: 50 professional emails
- **Monthly Reach**: 1,500 pet industry contacts
- **Response Rate**: 2-5% typical for cold outreach
- **Partnership Rate**: 0.5-1% conversion to paid advertising

## 🔧 Troubleshooting

### Common Issues

**"No contacts found"**
- Run scraper first: `python3 outreachscraper.py`
- Import contacts: `python3 email_outreach_system.py --import-contacts`

**"Email sending failed"**
- Check email configuration in `email_config.json`
- Verify API keys or SMTP credentials
- Test with: `python3 setup_email_system.py` → Option 2

**"Daily limit reached"**
- Check report: `python3 email_outreach_system.py --report`
- Limit resets daily at midnight
- Adjust limit in config file

### Email Service Setup

**Gmail SMTP Issues:**
- Use App Password, not regular password
- Enable 2-factor authentication
- Generate App Password at: https://myaccount.google.com/apppasswords

**SendGrid Issues:**
- Verify API key permissions
- Check sender authentication
- Review SendGrid activity dashboard

## 📁 File Structure

```
workspace/
├── outreachscraper.py              # Pet industry scraper
├── email_outreach_system.py        # Main email system
├── setup_email_system.py           # Interactive setup
├── email_config.json               # Email configuration
├── requirements.txt                # Dependencies
├── pet_industry_media_contacts.csv # Scraper output
├── email_outreach.db               # Contact database
├── email_outreach.log              # System logs
└── README.md                       # Main documentation
```

## 🎯 Next Steps

1. **Expand Contact Database**
   ```bash
   # Run scraper with more sites
   python3 outreachscraper.py --max-sites 200 --states-only "CA,NY,TX,FL"
   ```

2. **Customize Email Templates**
   - Edit templates in `email_outreach_system.py`
   - Add industry-specific messaging
   - Include case studies and testimonials

3. **Scale Up Gradually**
   - Start with 10-20 emails/day
   - Monitor deliverability and responses
   - Gradually increase to 50 emails/day

4. **Track Results**
   - Monitor open rates and responses
   - Update contact status in database
   - Refine templates based on feedback

## 🤝 Support

For questions or improvements:
- Check logs in `email_outreach.log`
- Review configuration in `email_config.json`
- Test email sending with setup script
- Monitor daily reports for campaign performance

**The system is now ready to automatically send 50 professional advertising outreach emails daily to pet industry publications! 🚀**