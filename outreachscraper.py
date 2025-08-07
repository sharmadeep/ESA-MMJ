#!/usr/bin/env python3
"""
Pet Industry Media Outreach Scraper

This script scrapes websites to find magazines and local newspapers 
related to the pet industry, extracting contact information for 
advertising outreach purposes.

Author: AI Assistant
"""

import requests
from bs4 import BeautifulSoup
import re
import csv
import json
import time
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import argparse
from dataclasses import dataclass
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pet_media_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContactInfo:
    """Data class for storing contact information"""
    publication_name: str
    website: str
    emails: List[str]
    phone_numbers: List[str]
    contact_page_url: str = ""
    advertising_info: str = ""
    description: str = ""
    category: str = ""  # magazine, newspaper, blog, etc.

class PetMediaScraper:
    """Main scraper class for finding pet industry media outlets"""
    
    def __init__(self, delay_range=(1, 3)):
        """Initialize the scraper with rate limiting"""
        self.delay_range = delay_range
        self.session = self._create_session()
        self.found_contacts = []
        self.visited_urls = set()
        
        # Email and phone regex patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}|\+?[0-9]{1,3}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4})')
        
        # Pet industry keywords for relevance checking
        self.pet_keywords = [
            'pet', 'dog', 'cat', 'animal', 'veterinary', 'vet', 'puppy', 'kitten',
            'petcare', 'pet care', 'animal health', 'pet food', 'pet supplies',
            'grooming', 'boarding', 'training', 'rescue', 'shelter', 'breed',
            'veterinarian', 'animal welfare', 'pet adoption', 'pet nutrition'
        ]
        
        # Target websites and search sources
        self.target_sources = [
            # Major pet industry publications
            'https://www.petproductnews.com',
            'https://www.petfoodindustry.com',
            'https://www.petbusiness.com',
            'https://www.americanpetproducts.org',
            'https://www.petage.com',
            
            # Search engines for finding local publications
            'https://www.google.com/search?q="pet+magazine"+contact+advertising',
            'https://www.google.com/search?q="animal+magazine"+contact+email',
            'https://www.google.com/search?q="local+pet+newspaper"+advertising',
            'https://www.google.com/search?q="veterinary+magazine"+contact',
        ]
        
        # Common contact page patterns
        self.contact_patterns = [
            'contact', 'about', 'advertising', 'media-kit', 'advertise',
            'contact-us', 'about-us', 'staff', 'editorial', 'business'
        ]

    def _create_session(self):
        """Create a requests session with retry strategy"""
        session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers to appear as a regular browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        return session

    def _delay(self):
        """Add random delay between requests"""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)

    def _is_pet_related(self, text: str) -> bool:
        """Check if content is related to pet industry"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.pet_keywords)

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        emails = self.email_pattern.findall(text)
        # Filter out common non-contact emails
        filtered_emails = []
        skip_patterns = ['noreply', 'no-reply', 'donotreply', 'support@', 'info@wordpress']
        
        for email in emails:
            if not any(pattern in email.lower() for pattern in skip_patterns):
                filtered_emails.append(email.lower())
        
        return list(set(filtered_emails))  # Remove duplicates

    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = self.phone_pattern.findall(text)
        # Clean and format phone numbers
        cleaned_phones = []
        for phone in phones:
            # Remove extra characters and format
            cleaned = re.sub(r'[^\d+]', '', phone)
            if len(cleaned) >= 10:  # Valid phone number length
                cleaned_phones.append(phone.strip())
        
        return list(set(cleaned_phones))  # Remove duplicates

    def _get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch and parse webpage content"""
        try:
            if url in self.visited_urls:
                return None
                
            self.visited_urls.add(url)
            logger.info(f"Fetching: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def _find_contact_pages(self, base_url: str, soup: BeautifulSoup) -> List[str]:
        """Find potential contact pages from navigation"""
        contact_urls = []
        
        if not soup:
            return contact_urls
            
        # Look for contact-related links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            # Check if link text or href contains contact keywords
            if any(pattern in href or pattern in text for pattern in self.contact_patterns):
                full_url = urljoin(base_url, link['href'])
                contact_urls.append(full_url)
        
        return list(set(contact_urls))

    def _extract_publication_info(self, url: str, soup: BeautifulSoup) -> Dict:
        """Extract publication information from webpage"""
        if not soup:
            return {}
            
        info = {
            'name': '',
            'description': '',
            'category': 'magazine'  # default
        }
        
        # Try to get publication name
        title_tag = soup.find('title')
        if title_tag:
            info['name'] = title_tag.get_text().strip()
        
        # Look for meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            info['description'] = meta_desc.get('content', '').strip()
        
        # Try to determine category based on content
        page_text = soup.get_text().lower()
        if 'newspaper' in page_text:
            info['category'] = 'newspaper'
        elif 'blog' in page_text:
            info['category'] = 'blog'
        elif 'journal' in page_text:
            info['category'] = 'journal'
            
        return info

    def scrape_website(self, url: str) -> ContactInfo:
        """Scrape a single website for contact information"""
        logger.info(f"Scraping website: {url}")
        
        # Get main page
        soup = self._get_page_content(url)
        if not soup:
            return None
            
        # Check if site is pet-related
        page_text = soup.get_text()
        if not self._is_pet_related(page_text):
            logger.info(f"Site not pet-related: {url}")
            return None
            
        # Extract basic info
        pub_info = self._extract_publication_info(url, soup)
        
        # Find contact pages
        contact_urls = self._find_contact_pages(url, soup)
        
        # Collect all text for contact extraction
        all_text = page_text
        advertising_info = ""
        
        # Scrape contact pages
        for contact_url in contact_urls[:3]:  # Limit to 3 contact pages
            self._delay()
            contact_soup = self._get_page_content(contact_url)
            if contact_soup:
                contact_text = contact_soup.get_text()
                all_text += " " + contact_text
                
                # Look for advertising-specific information
                if 'advertising' in contact_url.lower() or 'advertise' in contact_url.lower():
                    advertising_info = contact_text[:500]  # First 500 chars
        
        # Extract contact information
        emails = self._extract_emails(all_text)
        phones = self._extract_phone_numbers(all_text)
        
        if emails or phones:
            contact_info = ContactInfo(
                publication_name=pub_info.get('name', urlparse(url).netloc),
                website=url,
                emails=emails,
                phone_numbers=phones,
                contact_page_url=contact_urls[0] if contact_urls else "",
                advertising_info=advertising_info,
                description=pub_info.get('description', ''),
                category=pub_info.get('category', 'magazine')
            )
            
            logger.info(f"Found contact info for: {contact_info.publication_name}")
            return contact_info
        
        return None

    def search_google_for_publications(self, query: str, max_results: int = 10) -> List[str]:
        """Search Google for pet industry publications (simplified simulation)"""
        # Note: This is a simplified approach. In a real implementation,
        # you might want to use Google Custom Search API or other search APIs
        
        logger.info(f"Searching for: {query}")
        
        # Predefined list of known pet industry publications and local sources
        known_sources = [
            'https://www.petproductnews.com',
            'https://www.petfoodindustry.com',
            'https://www.petbusiness.com',
            'https://www.petage.com',
            'https://www.modernpetsupply.com',
            'https://www.petboardinginsurance.com',
            'https://www.groomernews.com',
            'https://www.todaysveterinarypractice.com',
            'https://www.veterinarypracticenews.com',
            'https://www.fetchdvm.com',
            'https://www.dvm360.com',
            'https://www.javma.com',
            'https://vetmag.com',
            'https://www.animalsheltering.org',
            'https://www.petrescue.com.au',
        ]
        
        return known_sources[:max_results]

    def run_scraper(self, max_sites: int = 20, output_format: str = 'csv'):
        """Run the complete scraping process"""
        logger.info("Starting pet industry media scraper...")
        
        # Search for publications
        search_queries = [
            "pet magazine contact advertising",
            "animal magazine editorial contact",
            "veterinary publication advertising",
            "local pet newspaper contact",
            "dog magazine advertising rates",
            "cat magazine contact information"
        ]
        
        all_urls = set()
        
        for query in search_queries:
            urls = self.search_google_for_publications(query, max_results=10)
            all_urls.update(urls)
            self._delay()
        
        # Add manual sources
        all_urls.update([
            'https://www.petproductnews.com',
            'https://www.petfoodindustry.com',
            'https://www.petbusiness.com',
            'https://www.petage.com',
        ])
        
        # Scrape each website
        scraped_count = 0
        for url in list(all_urls)[:max_sites]:
            if scraped_count >= max_sites:
                break
                
            try:
                contact_info = self.scrape_website(url)
                if contact_info:
                    self.found_contacts.append(contact_info)
                    scraped_count += 1
                    
                self._delay()
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        # Save results
        self.save_results(output_format)
        
        logger.info(f"Scraping completed. Found {len(self.found_contacts)} publications with contact info.")

    def save_results(self, format_type: str = 'csv'):
        """Save results to file"""
        if not self.found_contacts:
            logger.warning("No contacts found to save.")
            return
            
        if format_type.lower() == 'csv':
            self._save_csv()
        elif format_type.lower() == 'json':
            self._save_json()
        else:
            self._save_csv()
            self._save_json()

    def _save_csv(self):
        """Save results to CSV file"""
        filename = 'pet_industry_media_contacts.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Publication Name', 'Website', 'Category', 'Emails', 
                'Phone Numbers', 'Contact Page', 'Description', 'Advertising Info'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for contact in self.found_contacts:
                writer.writerow({
                    'Publication Name': contact.publication_name,
                    'Website': contact.website,
                    'Category': contact.category,
                    'Emails': '; '.join(contact.emails),
                    'Phone Numbers': '; '.join(contact.phone_numbers),
                    'Contact Page': contact.contact_page_url,
                    'Description': contact.description,
                    'Advertising Info': contact.advertising_info[:200] + '...' if len(contact.advertising_info) > 200 else contact.advertising_info
                })
        
        logger.info(f"Results saved to {filename}")

    def _save_json(self):
        """Save results to JSON file"""
        filename = 'pet_industry_media_contacts.json'
        
        data = []
        for contact in self.found_contacts:
            data.append({
                'publication_name': contact.publication_name,
                'website': contact.website,
                'category': contact.category,
                'emails': contact.emails,
                'phone_numbers': contact.phone_numbers,
                'contact_page_url': contact.contact_page_url,
                'description': contact.description,
                'advertising_info': contact.advertising_info
            })
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")

    def print_summary(self):
        """Print summary of found contacts"""
        if not self.found_contacts:
            print("No contacts found.")
            return
            
        print(f"\n{'='*60}")
        print(f"FOUND {len(self.found_contacts)} PET INDUSTRY PUBLICATIONS")
        print(f"{'='*60}")
        
        for i, contact in enumerate(self.found_contacts, 1):
            print(f"\n{i}. {contact.publication_name}")
            print(f"   Website: {contact.website}")
            print(f"   Category: {contact.category}")
            print(f"   Emails: {', '.join(contact.emails) if contact.emails else 'None found'}")
            print(f"   Phones: {', '.join(contact.phone_numbers) if contact.phone_numbers else 'None found'}")
            if contact.description:
                print(f"   Description: {contact.description[:100]}...")

def main():
    """Main function to run the scraper"""
    parser = argparse.ArgumentParser(description='Pet Industry Media Outreach Scraper')
    parser.add_argument('--max-sites', type=int, default=20, help='Maximum number of sites to scrape')
    parser.add_argument('--output', choices=['csv', 'json', 'both'], default='csv', help='Output format')
    parser.add_argument('--delay-min', type=float, default=1.0, help='Minimum delay between requests (seconds)')
    parser.add_argument('--delay-max', type=float, default=3.0, help='Maximum delay between requests (seconds)')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = PetMediaScraper(delay_range=(args.delay_min, args.delay_max))
    
    # Run scraping
    scraper.run_scraper(max_sites=args.max_sites, output_format=args.output)
    
    # Print summary
    scraper.print_summary()

if __name__ == "__main__":
    main()
