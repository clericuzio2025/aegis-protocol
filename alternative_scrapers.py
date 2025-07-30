#!/usr/bin/env python3
"""
Alternative scraping modules for battery buyers
"""

import re
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

class AlternativeScrapers:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
    
    def get_random_headers(self):
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def extract_contact_info(self, text):
        """Extract phone numbers and emails from text"""
        phone_pattern = r'(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})'
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        phones = re.findall(phone_pattern, text)
        emails = re.findall(email_pattern, text)
        
        # Clean phone numbers
        cleaned_phones = []
        for phone in phones:
            cleaned = re.sub(r'[^\d]', '', phone)
            if len(cleaned) == 10:
                cleaned_phones.append(f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}")
            elif len(cleaned) == 11 and cleaned[0] == '1':
                cleaned_phones.append(f"({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}")
        
        return cleaned_phones, emails
    
    def scrape_craigslist_services(self, city_code='newyork'):
        """Scrape Craigslist services for battery buyers"""
        buyers = []
        
        try:
            # Search for battery-related services
            search_terms = ['battery', 'scrap', 'recycling', 'lead']
            
            for term in search_terms[:2]:  # Limit searches
                url = f"https://{city_code}.craigslist.org/search/bts"
                params = {'query': term}
                
                headers = self.get_random_headers()
                response = self.session.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find listing items
                    listings = soup.find_all('li', class_='result-row')[:2]  # Limit results
                    
                    for listing in listings:
                        try:
                            title_elem = listing.find('a', class_='result-title')
                            if not title_elem:
                                continue
                            
                            title = title_elem.get_text(strip=True)
                            
                            # Check if it's battery-related
                            battery_keywords = ['battery', 'scrap', 'lead', 'recycl', 'buyer', 'purchase']
                            if any(keyword in title.lower() for keyword in battery_keywords):
                                
                                # Try to get the detail page for contact info
                                detail_url = title_elem.get('href', '')
                                if detail_url.startswith('/'):
                                    detail_url = f"https://{city_code}.craigslist.org{detail_url}"
                                
                                # Get contact info from detail page
                                detail_response = self.session.get(detail_url, headers=headers, timeout=5)
                                if detail_response.status_code == 200:
                                    detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                                    detail_text = detail_soup.get_text()
                                    
                                    phones, emails = self.extract_contact_info(detail_text)
                                    
                                    if phones or emails:
                                        buyers.append({
                                            'company_name': title,
                                            'phone': phones[0] if phones else '',
                                            'email': emails[0] if emails else '',
                                            'website': detail_url,
                                            'business_type': 'Classified Ad',
                                            'confidence_score': 0.4,
                                            'source_url': detail_url
                                        })
                                
                                time.sleep(random.uniform(1, 3))  # Rate limiting
                                
                        except Exception as e:
                            logger.warning(f"Error parsing Craigslist listing: {e}")
                
                time.sleep(random.uniform(2, 4))
                
        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")
        
        return buyers
    
    def scrape_recycling_centers(self):
        """Scrape general recycling center directories"""
        buyers = []
        
        # Search terms that might find battery recyclers
        recycling_sites = [
            "https://earth911.com/recycling-center-search-guides/",
            "https://www.call2recycle.org/locator/",
        ]
        
        for site_url in recycling_sites:
            try:
                headers = self.get_random_headers()
                response = self.session.get(site_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    text = soup.get_text()
                    
                    # Look for contact patterns near battery-related keywords
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if any(keyword in line.lower() for keyword in ['battery', 'lead', 'automotive']):
                            # Look for contact info in nearby lines
                            search_range = lines[max(0, i-3):min(len(lines), i+4)]
                            search_text = '\n'.join(search_range)
                            
                            phones, emails = self.extract_contact_info(search_text)
                            
                            if phones:
                                # Try to find a company name
                                potential_names = [l.strip() for l in search_range if l.strip() and len(l.strip()) > 5 and len(l.strip()) < 60]
                                company_name = potential_names[0] if potential_names else 'Recycling Center'
                                
                                buyers.append({
                                    'company_name': company_name,
                                    'phone': phones[0],
                                    'email': emails[0] if emails else '',
                                    'website': site_url,
                                    'business_type': 'Recycling Center',
                                    'confidence_score': 0.5,
                                    'source_url': site_url
                                })
                                break  # Only take one per site
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.warning(f"Error scraping recycling site {site_url}: {e}")
        
        return buyers
    
    def scrape_business_directories(self, search_term, state='NY'):
        """Scrape alternative business directories"""
        buyers = []
        
        # List of alternative directory sites
        directories = [
            f"https://www.superpages.com/search?search_terms={search_term}&geo_location_terms={state}",
            f"https://www.whitepages.com/business/search?utf8=%E2%9C%93&search_where={state}&search_what={search_term}",
        ]
        
        for directory_url in directories:
            try:
                headers = self.get_random_headers()
                response = self.session.get(directory_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for business listings with various selectors
                    listing_selectors = [
                        '.listing', '.result', '.business-listing', 
                        '.search-result', '.directory-listing'
                    ]
                    
                    listings = []
                    for selector in listing_selectors:
                        found = soup.select(selector)[:2]  # Limit results
                        if found:
                            listings = found
                            break
                    
                    for listing in listings:
                        try:
                            # Extract business name
                            name_selectors = ['h3', 'h2', '.business-name', '.name', '.title']
                            company_name = ''
                            for selector in name_selectors:
                                name_elem = listing.select_one(selector)
                                if name_elem:
                                    company_name = name_elem.get_text(strip=True)
                                    break
                            
                            if not company_name:
                                continue
                            
                            # Extract contact info from listing text
                            listing_text = listing.get_text()
                            phones, emails = self.extract_contact_info(listing_text)
                            
                            if phones:
                                buyers.append({
                                    'company_name': company_name,
                                    'phone': phones[0],
                                    'email': emails[0] if emails else '',
                                    'website': directory_url,
                                    'business_type': 'Business Directory',
                                    'confidence_score': 0.6,
                                    'source_url': directory_url
                                })
                        
                        except Exception as e:
                            logger.warning(f"Error parsing directory listing: {e}")
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.warning(f"Error scraping directory {directory_url}: {e}")
        
        return buyers
    
    def scrape_metal_scrap_yards(self):
        """Scrape scrap metal yards that might buy batteries"""
        buyers = []
        
        try:
            # Search for scrap yards
            url = "https://www.iscrapapp.com/scrap-yard/united-states"
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for scrap yard listings
                listings = soup.find_all('div', class_=['scrap-yard', 'listing'])[:3]  # Limit results
                
                for listing in listings:
                    try:
                        # Extract business info
                        name_elem = listing.find(['h3', 'h2', 'h4'])
                        if not name_elem:
                            continue
                        
                        company_name = name_elem.get_text(strip=True)
                        
                        # Check if they mention batteries
                        listing_text = listing.get_text()
                        if any(keyword in listing_text.lower() for keyword in ['battery', 'lead', 'automotive']):
                            
                            phones, emails = self.extract_contact_info(listing_text)
                            
                            if phones:
                                buyers.append({
                                    'company_name': company_name,
                                    'phone': phones[0],
                                    'email': emails[0] if emails else '',
                                    'website': url,
                                    'business_type': 'Scrap Metal Yard',
                                    'confidence_score': 0.7,
                                    'source_url': url
                                })
                    
                    except Exception as e:
                        logger.warning(f"Error parsing scrap yard listing: {e}")
            
            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            logger.error(f"Error scraping scrap yards: {e}")
        
        return buyers