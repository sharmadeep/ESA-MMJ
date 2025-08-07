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
        
        # US States for local publication search
        self.us_states = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
            'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
            'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
            'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
            'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
            'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
            'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
            'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
            'DC': 'District of Columbia'
        }
        
        # Major US cities for targeted local search
        self.major_cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis', 'Seattle',
            'Denver', 'Washington', 'Boston', 'El Paso', 'Nashville', 'Detroit', 'Oklahoma City',
            'Portland', 'Las Vegas', 'Memphis', 'Louisville', 'Baltimore', 'Milwaukee',
            'Albuquerque', 'Tucson', 'Fresno', 'Sacramento', 'Mesa', 'Kansas City', 'Atlanta',
            'Long Beach', 'Colorado Springs', 'Raleigh', 'Miami', 'Virginia Beach', 'Omaha',
            'Oakland', 'Minneapolis', 'Tulsa', 'Arlington', 'Tampa', 'New Orleans'
        ]
        
        # Target websites and search sources
        self.target_sources = [
            # Major pet industry publications
            'https://www.petproductnews.com',
            'https://www.petfoodindustry.com',
            'https://www.petbusiness.com',
            'https://www.americanpetproducts.org',
            'https://www.petage.com',
        ]
        
        # Local newspaper and magazine patterns
        self.local_publication_sources = [
            # General pet industry sites that might list local publications
            'https://www.newspapers.com',
            'https://usnpl.com',  # US Newspaper List
            'https://www.4imn.com/us/',  # US newspapers by state
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

    def get_state_specific_sources(self, state_code: str, state_name: str) -> List[str]:
        """Generate state-specific publication sources"""
        sources = []
        
        # Common local publication patterns by state
        state_domains = [
            f"https://www.{state_name.lower().replace(' ', '')}.com",
            f"https://www.{state_code.lower()}.gov/news",
            f"https://www.{state_name.lower().replace(' ', '')}news.com",
            f"https://www.{state_name.lower().replace(' ', '')}magazine.com",
            f"https://www.{state_name.lower().replace(' ', '')}pets.com",
            f"https://www.{state_name.lower().replace(' ', '')}animals.com",
        ]
        
        # Known state-specific pet publications (examples)
        state_specific_pubs = {
            'CA': [
                'https://www.californiapetmagazine.com',
                'https://www.dogster.com',
                'https://www.moderndog.com',
                'https://www.petsbest.com',
            ],
            'TX': [
                'https://www.texaspetcompany.com',
                'https://www.dogtown.com',
                'https://www.texasmonthly.com/category/pets/',
            ],
            'NY': [
                'https://www.nymag.com/strategist/pets',
                'https://www.timeout.com/newyork/pets',
                'https://www.newyorker.com/tag/pets',
            ],
            'FL': [
                'https://www.floridapetmagazine.com',
                'https://www.southfloridapets.com',
                'https://www.pawprint.net',
            ],
            'IL': [
                'https://www.chicagomag.com/pets/',
                'https://www.pawschicago.org',
                'https://www.illinois.gov/news/pets',
            ],
        }
        
        if state_code in state_specific_pubs:
            sources.extend(state_specific_pubs[state_code])
        
        return sources

    def get_city_specific_sources(self, city: str, state: str = "") -> List[str]:
        """Generate city-specific publication sources"""
        city_clean = city.lower().replace(' ', '')
        sources = []
        
        # Common city publication patterns
        city_patterns = [
            f"https://www.{city_clean}magazine.com",
            f"https://www.{city_clean}pets.com",
            f"https://www.{city_clean}animals.com",
            f"https://www.{city_clean}news.com",
            f"https://www.{city_clean}weekly.com",
            f"https://www.{city_clean}petguide.com",
        ]
        
        sources.extend(city_patterns)
        
        # Known city-specific publications
        city_pubs = {
            'new york': [
                'https://www.timeout.com/newyork/pets',
                'https://ny1.com/nyc/all-boroughs/pets',
                'https://www.amny.com/lifestyle/pets/',
            ],
            'los angeles': [
                'https://www.laweekly.com/tag/pets/',
                'https://la.curbed.com/pets',
                'https://www.latimes.com/lifestyle/pets',
            ],
            'chicago': [
                'https://www.chicagomag.com/pets/',
                'https://www.timeout.com/chicago/pets',
                'https://chicago.suntimes.com/pets',
            ],
            'houston': [
                'https://www.houstonchronicle.com/lifestyle/pets/',
                'https://www.houstonpetmagazine.com',
                'https://www.houstoniamag.com/pets/',
            ],
            'philadelphia': [
                'https://www.phillymag.com/pets/',
                'https://www.inquirer.com/pets/',
                'https://www.metro.us/philadelphia/pets/',
            ],
        }
        
        city_lower = city.lower()
        if city_lower in city_pubs:
            sources.extend(city_pubs[city_lower])
        
        return sources

    def search_for_publications_by_location(self, location_type: str = "state", max_results: int = 5) -> List[str]:
        """Search for publications by US states and cities"""
        all_sources = set()
        
        if location_type == "state":
            # Search by state
            for state_code, state_name in list(self.us_states.items())[:10]:  # Limit for demo
                logger.info(f"Searching publications in {state_name}")
                state_sources = self.get_state_specific_sources(state_code, state_name)
                all_sources.update(state_sources[:max_results])
                self._delay()
        
        elif location_type == "city":
            # Search by major cities
            for city in self.major_cities[:15]:  # Limit for demo
                logger.info(f"Searching publications in {city}")
                city_sources = self.get_city_specific_sources(city)
                all_sources.update(city_sources[:max_results])
                self._delay()
        
        return list(all_sources)

    def search_google_for_publications(self, query: str, max_results: int = 10) -> List[str]:
        """Search for pet industry publications with enhanced local search"""
        logger.info(f"Searching for: {query}")
        
        # National pet industry publications
        national_sources = [
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
            'https://www.aspca.org',
            'https://www.humanesociety.org',
            'https://www.avma.org',
            'https://www.appa.org',
            'https://www.petfoodinsitute.org',
            'https://www.americanpetproducts.org',
        ]
        
        # Veterinary and professional publications
        vet_sources = [
            'https://www.dvm360.com',
            'https://www.veterinarypracticenews.com',
            'https://www.todaysveterinarypractice.com',
            'https://www.javma.avma.org',
            'https://www.veterinaryteambrief.com',
            'https://www.cliniciansbrief.com',
            'https://www.vin.com',
            'https://www.vetfolio.com',
            'https://www.myvmc.com',
            'https://www.veterinaryadvantage.com',
        ]
        
        # Pet specialty publications
        specialty_sources = [
            'https://www.dogfancymagazine.com',
            'https://www.catfancymagazine.com',
            'https://www.birdtalk.com',
            'https://www.reptilemagazine.com',
            'https://www.freshwateraquariummagazine.com',
            'https://www.horseandridermag.com',
            'https://www.groomingbusiness.com',
            'https://www.petproductmarketing.com',
            'https://www.petretailer.com',
            'https://www.petstoremagazine.com',
        ]
        
        all_sources = national_sources + vet_sources + specialty_sources
        return all_sources[:max_results]

    def run_scraper(self, max_sites: int = 100, output_format: str = 'csv', include_local: bool = True):
        """Run the complete scraping process with US-wide coverage"""
        logger.info("Starting comprehensive US pet industry media scraper...")
        
        all_urls = set()
        
        # 1. National publications search
        logger.info("Searching national pet industry publications...")
        search_queries = [
            "pet magazine contact advertising",
            "animal magazine editorial contact", 
            "veterinary publication advertising",
            "pet industry magazine contact",
            "dog magazine advertising rates",
            "cat magazine contact information"
        ]
        
        for query in search_queries:
            urls = self.search_google_for_publications(query, max_results=15)
            all_urls.update(urls)
            self._delay()
        
        # 2. State-by-state local publications
        if include_local:
            logger.info("Searching state-by-state for local pet publications...")
            state_urls = self.search_for_publications_by_location("state", max_results=3)
            all_urls.update(state_urls)
            
            # 3. Major cities publications  
            logger.info("Searching major cities for local pet publications...")
            city_urls = self.search_for_publications_by_location("city", max_results=2)
            all_urls.update(city_urls)
            
            # 4. Generate state-specific search patterns
            logger.info("Generating comprehensive state-specific URLs...")
            for state_code, state_name in self.us_states.items():
                # State-specific pet publication patterns
                state_patterns = [
                    f"https://www.{state_name.lower().replace(' ', '')}petmagazine.com",
                    f"https://www.{state_name.lower().replace(' ', '')}pets.com", 
                    f"https://www.{state_name.lower().replace(' ', '')}animals.org",
                    f"https://www.{state_name.lower().replace(' ', '')}veterinary.com",
                    f"https://www.{state_code.lower()}pets.com",
                    f"https://www.{state_code.lower()}animals.com",
                ]
                all_urls.update(state_patterns)
        
        # 5. Add specialized pet industry sources
        specialized_sources = self._get_specialized_sources()
        all_urls.update(specialized_sources)
        
        # 6. Add local newspaper sources that might have pet sections
        newspaper_sources = self._get_local_newspaper_sources()
        all_urls.update(newspaper_sources)
        
        logger.info(f"Total URLs to scrape: {len(all_urls)}")
        
        # Scrape each website
        scraped_count = 0
        successful_scrapes = 0
        
        for url in list(all_urls)[:max_sites]:
            if scraped_count >= max_sites:
                break
                
            try:
                contact_info = self.scrape_website(url)
                if contact_info:
                    self.found_contacts.append(contact_info)
                    successful_scrapes += 1
                    logger.info(f"Success: Found contacts for {contact_info.publication_name}")
                    
                scraped_count += 1
                self._delay()
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                scraped_count += 1
                continue
        
        # Save results
        self.save_results(output_format)
        
        logger.info(f"Scraping completed. Scraped {scraped_count} sites, found {successful_scrapes} publications with contact info.")

    def _get_specialized_sources(self) -> List[str]:
        """Get specialized pet industry publication sources"""
        return [
            # Pet industry trade publications
            'https://www.petproductnews.com',
            'https://www.petfoodindustry.com', 
            'https://www.petbusiness.com',
            'https://www.petage.com',
            'https://www.groomernews.com',
            'https://www.petboardinginsurance.com',
            
            # Veterinary publications
            'https://www.dvm360.com',
            'https://www.veterinarypracticenews.com',
            'https://www.todaysveterinarypractice.com',
            'https://www.javma.avma.org',
            'https://www.veterinaryteambrief.com',
            'https://www.cliniciansbrief.com',
            
            # Pet specialty magazines
            'https://www.dogfancymagazine.com',
            'https://www.catfancymagazine.com', 
            'https://www.moderndogmagazine.com',
            'https://www.catster.com',
            'https://www.dogster.com',
            
            # Animal welfare publications
            'https://www.animalsheltering.org',
            'https://www.aspca.org',
            'https://www.humanesociety.org',
            'https://www.petfinder.com',
            'https://www.adopt-a-pet.com',
            
            # Pet business publications
            'https://www.petretailer.com',
            'https://www.petstoremagazine.com',
            'https://www.groomingbusiness.com',
            'https://www.petproductmarketing.com',
        ]

    def _get_local_newspaper_sources(self) -> List[str]:
        """Get local newspaper sources that might have pet sections"""
        sources = []
        
        # Major newspaper chains that often have pet sections
        newspaper_chains = [
            'gannett.com', 'mcclatchy.com', 'hearst.com', 'tribune.com',
            'advance.com', 'gatehouse.com', 'newscorp.com'
        ]
        
        # Generate URLs for major cities' newspapers
        for city in self.major_cities[:25]:  # Top 25 cities
            city_clean = city.lower().replace(' ', '')
            newspaper_patterns = [
                f"https://www.{city_clean}news.com",
                f"https://www.{city_clean}times.com", 
                f"https://www.{city_clean}herald.com",
                f"https://www.{city_clean}post.com",
                f"https://www.{city_clean}gazette.com",
                f"https://www.{city_clean}tribune.com",
                f"https://www.{city_clean}weekly.com",
                f"https://www.{city_clean}daily.com",
            ]
            sources.extend(newspaper_patterns)
        
        return sources

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
    parser = argparse.ArgumentParser(description='Pet Industry Media Outreach Scraper - US-Wide Coverage')
    parser.add_argument('--max-sites', type=int, default=100, help='Maximum number of sites to scrape')
    parser.add_argument('--output', choices=['csv', 'json', 'both'], default='csv', help='Output format')
    parser.add_argument('--delay-min', type=float, default=1.0, help='Minimum delay between requests (seconds)')
    parser.add_argument('--delay-max', type=float, default=3.0, help='Maximum delay between requests (seconds)')
    parser.add_argument('--no-local', action='store_true', help='Skip local/state-specific publications')
    parser.add_argument('--states-only', help='Comma-separated list of state codes to focus on (e.g., CA,NY,TX)')
    parser.add_argument('--cities-only', help='Comma-separated list of cities to focus on (e.g., "New York,Los Angeles")')
    
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = PetMediaScraper(delay_range=(args.delay_min, args.delay_max))
    
    # Handle state-specific filtering
    if args.states_only:
        state_codes = [s.strip().upper() for s in args.states_only.split(',')]
        # Filter to only requested states
        scraper.us_states = {k: v for k, v in scraper.us_states.items() if k in state_codes}
        logger.info(f"Focusing on states: {', '.join(state_codes)}")
    
    # Handle city-specific filtering  
    if args.cities_only:
        cities = [c.strip() for c in args.cities_only.split(',')]
        scraper.major_cities = cities
        logger.info(f"Focusing on cities: {', '.join(cities)}")
    
    # Run scraping
    include_local = not args.no_local
    scraper.run_scraper(
        max_sites=args.max_sites, 
        output_format=args.output,
        include_local=include_local
    )
    
    # Print summary
    scraper.print_summary()

if __name__ == "__main__":
    main()
