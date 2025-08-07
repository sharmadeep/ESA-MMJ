# Pet Industry Media Outreach Scraper - US-Wide Coverage

A comprehensive web scraper designed to find magazines, local newspapers, and digital publications related to the pet industry across all US states for advertising outreach purposes.

## Features

- **National Coverage**: Scrapes pet industry publications across all 50 US states + DC
- **Local Publications**: Finds state-specific and city-specific pet magazines and newspapers
- **Contact Extraction**: Automatically extracts email addresses and phone numbers
- **Multiple Output Formats**: Saves results in CSV and JSON formats
- **Responsible Scraping**: Built-in rate limiting and error handling
- **Targeted Search**: Focus on specific states or cities
- **Comprehensive Database**: Includes national publications, veterinary journals, specialty magazines, and local newspapers

## Installation

1. Clone or download the repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings (100 sites, CSV output):

```bash
python outreachscraper.py
```

### Advanced Usage Examples

**Scrape specific states only:**
```bash
python outreachscraper.py --states-only "CA,NY,TX,FL" --max-sites 150
```

**Focus on major cities:**
```bash
python outreachscraper.py --cities-only "New York,Los Angeles,Chicago,Houston" --max-sites 80
```

**National publications only (skip local):**
```bash
python outreachscraper.py --no-local --max-sites 50
```

**Custom output format:**
```bash
python outreachscraper.py --output both --max-sites 200
```

**Adjust scraping speed:**
```bash
python outreachscraper.py --delay-min 2.0 --delay-max 5.0
```

### Command Line Arguments

- `--max-sites`: Maximum number of websites to scrape (default: 100)
- `--output`: Output format - 'csv', 'json', or 'both' (default: csv)
- `--delay-min`: Minimum delay between requests in seconds (default: 1.0)
- `--delay-max`: Maximum delay between requests in seconds (default: 3.0)
- `--no-local`: Skip local/state-specific publications, national only
- `--states-only`: Comma-separated state codes (e.g., "CA,NY,TX")
- `--cities-only`: Comma-separated city names (e.g., "New York,Los Angeles")

## Output Files

The scraper generates the following files:

### CSV Output (`pet_industry_media_contacts.csv`)
Contains columns:
- Publication Name
- Website
- Category (magazine, newspaper, blog, journal)
- Emails (semicolon-separated)
- Phone Numbers (semicolon-separated)
- Contact Page URL
- Description
- Advertising Info

### JSON Output (`pet_industry_media_contacts.json`)
Structured JSON with the same information in array format.

### Log File (`pet_media_scraper.log`)
Detailed logging of the scraping process for debugging and monitoring.

## Publication Categories Covered

### National Pet Industry Publications
- Pet Product News
- Pet Food Industry Magazine
- Pet Business Magazine
- Pet Age Magazine
- Groomer News

### Veterinary Publications
- DVM 360
- Veterinary Practice News
- Today's Veterinary Practice
- Journal of the American Veterinary Medical Association
- Veterinary Team Brief

### Pet Specialty Magazines
- Dog Fancy Magazine
- Cat Fancy Magazine
- Modern Dog Magazine
- Catster
- Dogster

### Animal Welfare Publications
- Animal Sheltering Magazine
- ASPCA Publications
- Humane Society Publications

### Local & Regional Coverage
- State-specific pet magazines
- City newspapers with pet sections
- Regional animal welfare publications
- Local veterinary newsletters

## US States Covered

All 50 states plus Washington DC:
- Alabama, Alaska, Arizona, Arkansas, California, Colorado, Connecticut, Delaware
- Florida, Georgia, Hawaii, Idaho, Illinois, Indiana, Iowa, Kansas, Kentucky
- Louisiana, Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi
- Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey, New Mexico
- New York, North Carolina, North Dakota, Ohio, Oklahoma, Oregon, Pennsylvania
- Rhode Island, South Carolina, South Dakota, Tennessee, Texas, Utah, Vermont
- Virginia, Washington, West Virginia, Wisconsin, Wyoming, District of Columbia

## Major Cities Targeted

50+ major US cities including:
- New York, Los Angeles, Chicago, Houston, Phoenix, Philadelphia
- San Antonio, San Diego, Dallas, San Jose, Austin, Jacksonville
- Fort Worth, Columbus, Charlotte, San Francisco, Indianapolis, Seattle
- Denver, Washington DC, Boston, El Paso, Nashville, Detroit
- And many more...

## Contact Information Extracted

### Email Types
- Editorial contacts
- Advertising contacts  
- Business development emails
- General inquiry emails
- Publisher contacts

### Phone Numbers
- Main office numbers
- Advertising department
- Editorial department
- Direct contact numbers

## Responsible Scraping Features

- **Rate Limiting**: Configurable delays between requests
- **Error Handling**: Graceful handling of failed requests
- **Retry Logic**: Automatic retries for temporary failures
- **User Agent Rotation**: Appears as regular browser traffic
- **Respect for robots.txt**: (Note: Always check robots.txt manually for important sites)

## Sample Output

```csv
Publication Name,Website,Category,Emails,Phone Numbers,Contact Page,Description,Advertising Info
Pet Product News,https://www.petproductnews.com,magazine,editor@petproductnews.com; ads@petproductnews.com,(555) 123-4567,https://www.petproductnews.com/contact,Leading pet industry trade publication,Full advertising packages available...
California Pet Magazine,https://www.californiapetmagazine.com,magazine,info@californiapetmagazine.com,(555) 987-6543,https://www.californiapetmagazine.com/advertise,California's premier pet lifestyle magazine,Digital and print advertising options...
```

## Tips for Best Results

1. **Start Small**: Test with `--max-sites 20` first to validate results
2. **Focus Locally**: Use `--states-only` for your target geographic area
3. **Check Logs**: Monitor the log file for any issues or blocked sites
4. **Verify Contacts**: Always verify contact information before outreach
5. **Respect Websites**: Use appropriate delays and don't overwhelm servers

## Legal and Ethical Considerations

- This tool is for legitimate business outreach purposes only
- Always comply with website terms of service
- Respect rate limits and robots.txt files
- Verify contact information before use
- Follow CAN-SPAM Act requirements for email outreach
- Consider reaching out through official contact forms when available

## Troubleshooting

**No results found:**
- Check your internet connection
- Verify the target websites are accessible
- Try reducing the delay times
- Check the log file for specific errors

**Few contacts extracted:**
- Some sites may not have easily accessible contact info
- Try increasing `--max-sites` to cast a wider net
- Check if sites are blocking automated access

**Slow performance:**
- Reduce `--delay-min` and `--delay-max` (but be respectful)
- Use `--no-local` to focus on national publications only
- Limit to specific states with `--states-only`

## Contributing

This scraper can be enhanced with:
- Additional publication sources
- Better contact extraction patterns
- Integration with search APIs
- Improved geographic targeting
- Social media contact discovery

## License

This tool is provided for educational and legitimate business purposes. Users are responsible for ensuring compliance with all applicable laws and website terms of service.