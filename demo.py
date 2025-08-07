#!/usr/bin/env python3
"""
Demo script for the Pet Industry Media Scraper
Tests functionality with a limited set of known publications
"""

from outreachscraper import PetMediaScraper
import logging

# Configure logging for demo
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_scraper():
    """Run a demonstration of the scraper with known pet industry sites"""
    
    print("=" * 60)
    print("PET INDUSTRY MEDIA SCRAPER - DEMO")
    print("=" * 60)
    
    # Initialize scraper with faster settings for demo
    scraper = PetMediaScraper(delay_range=(0.5, 1.0))
    
    # Test with a few known pet industry sites
    test_sites = [
        'https://www.petproductnews.com',
        'https://www.petfoodindustry.com', 
        'https://www.petage.com',
        'https://www.dvm360.com',
        'https://www.aspca.org',
    ]
    
    print(f"Testing with {len(test_sites)} known pet industry websites...")
    print("This demo will attempt to extract contact information from:")
    for i, site in enumerate(test_sites, 1):
        print(f"  {i}. {site}")
    print()
    
    # Scrape each test site
    for site in test_sites:
        try:
            print(f"Scraping: {site}")
            contact_info = scraper.scrape_website(site)
            
            if contact_info:
                print(f"✓ SUCCESS: Found contact info for {contact_info.publication_name}")
                print(f"  Category: {contact_info.category}")
                print(f"  Emails: {', '.join(contact_info.emails) if contact_info.emails else 'None found'}")
                print(f"  Phones: {', '.join(contact_info.phone_numbers) if contact_info.phone_numbers else 'None found'}")
                scraper.found_contacts.append(contact_info)
            else:
                print(f"✗ No contact info found for {site}")
                
        except Exception as e:
            print(f"✗ ERROR scraping {site}: {str(e)}")
        
        print("-" * 40)
    
    # Save results if any found
    if scraper.found_contacts:
        print(f"\nSaving results for {len(scraper.found_contacts)} publications...")
        scraper.save_results('both')  # Save both CSV and JSON
        print("Results saved to:")
        print("  - pet_industry_media_contacts.csv")
        print("  - pet_industry_media_contacts.json")
    else:
        print("\nNo contact information found in demo.")
    
    # Print summary
    print("\n" + "=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    scraper.print_summary()
    
    print("\nTo run the full scraper with US-wide coverage:")
    print("  python outreachscraper.py --max-sites 100")
    print("\nTo focus on specific states:")
    print("  python outreachscraper.py --states-only 'CA,NY,TX'")

if __name__ == "__main__":
    demo_scraper()