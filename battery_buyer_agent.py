#!/usr/bin/env python3
"""
Scrap Battery Buyer Finder Agent
A novel agent that finds scrap battery buyers without APIs
"""

import os
import re
import time
import random
import sqlite3
import logging
import schedule
import requests
import threading
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask, render_template, jsonify, request
import pandas as pd
from alternative_scrapers import AlternativeScrapers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('battery_buyer_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatteryBuyerAgent:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.db_path = 'battery_buyers.db'
        self.init_database()
        self.alt_scrapers = AlternativeScrapers()
        self.search_terms = [
            "scrap battery buyers",
            "battery recycling companies",
            "lead battery scrap dealers",
            "automotive battery recyclers",
            "industrial battery buyers",
            "battery scrap yard",
            "lead acid battery recycling",
            "battery disposal services",
            "scrap metal battery buyers",
            "battery core buyers"
        ]
        self.cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin",
            "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "Detroit",
            "Memphis", "Boston", "Seattle", "Denver", "Nashville",
            "Portland", "Las Vegas", "Louisville", "Baltimore", "Milwaukee"
        ]
        self.current_city_index = 0
        self.current_term_index = 0
        
    def init_database(self):
        """Initialize SQLite database for storing buyer information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buyers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                email TEXT,
                website TEXT,
                business_type TEXT,
                city TEXT,
                state TEXT,
                confidence_score REAL,
                source_url TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(company_name, phone, address)
            )
        ''')
        
        conn.commit()
        conn.close()
        
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
    
    def scrape_yellowpages(self, search_term, city):
        """Scrape Yellow Pages for battery buyers"""
        buyers = []
        
        try:
            url = f"https://www.yellowpages.com/search"
            params = {
                'search_terms': search_term,
                'geo_location_terms': city
            }
            
            headers = self.get_random_headers()
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find business listings
                listings = soup.find_all('div', class_=['result', 'organic'])
                
                for listing in listings[:3]:  # Limit to first 3 results
                    try:
                        name_elem = listing.find('a', class_=['business-name', 'n'])
                        if not name_elem:
                            continue
                            
                        company_name = name_elem.get_text(strip=True)
                        
                        # Get phone number
                        phone_elem = listing.find('div', class_=['phones', 'phone'])
                        phone = phone_elem.get_text(strip=True) if phone_elem else ''
                        
                        # Get address
                        address_elem = listing.find('div', class_=['adr', 'street-address'])
                        address = address_elem.get_text(strip=True) if address_elem else ''
                        
                        # Get website
                        website_elem = listing.find('a', class_=['track-visit-website'])
                        website = website_elem.get('href', '') if website_elem else ''
                        
                        if company_name and (phone or address):
                            buyers.append({
                                'company_name': company_name,
                                'phone': phone,
                                'address': address,
                                'website': website,
                                'city': city,
                                'business_type': 'Directory Listing',
                                'confidence_score': 0.7,
                                'source_url': response.url
                            })
                            
                    except Exception as e:
                        logger.warning(f"Error parsing Yellow Pages listing: {e}")
                        
            time.sleep(random.uniform(2, 4))  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error scraping Yellow Pages: {e}")
            
        return buyers
    
    def scrape_google_business(self, search_term, city):
        """Scrape Google Business listings using Selenium"""
        buyers = []
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'--user-agent={self.ua.random}')
            
            driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
            
            query = f"{search_term} {city}"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            driver.get(url)
            time.sleep(3)
            
            # Look for business listings
            business_elements = driver.find_elements(By.CSS_SELECTOR, '[data-attrid="kc:/business:phone"]')
            
            for elem in business_elements[:2]:  # Limit results
                try:
                    # Navigate up to find the business container
                    business_container = elem.find_element(By.XPATH, './ancestor::div[contains(@class, "g")]')
                    
                    # Extract business name
                    name_elem = business_container.find_element(By.CSS_SELECTOR, 'h3')
                    company_name = name_elem.text if name_elem else ''
                    
                    # Extract phone
                    phone = elem.text
                    
                    # Extract address (if available)
                    try:
                        address_elem = business_container.find_element(By.CSS_SELECTOR, '[data-attrid="kc:/business:address"]')
                        address = address_elem.text
                    except:
                        address = ''
                    
                    if company_name and phone:
                        buyers.append({
                            'company_name': company_name,
                            'phone': phone,
                            'address': address,
                            'website': '',
                            'city': city,
                            'business_type': 'Google Business',
                            'confidence_score': 0.8,
                            'source_url': url
                        })
                        
                except Exception as e:
                    logger.warning(f"Error parsing Google business result: {e}")
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping Google Business: {e}")
            
        return buyers
    
    def scrape_industry_directories(self, search_term):
        """Scrape industry-specific directories"""
        buyers = []
        
        # List of industry directory URLs to check
        directories = [
            "https://www.recyclingtoday.com/directories/",
            "https://www.waste360.com/directory",
            "https://www.batteriesplus.com/t-battery-recycling",
        ]
        
        for directory_url in directories:
            try:
                headers = self.get_random_headers()
                response = self.session.get(directory_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for contact information patterns
                    text = soup.get_text()
                    phones, emails = self.extract_contact_info(text)
                    
                    # Find company names near contact info
                    for phone in phones[:1]:  # Limit to 1 per directory
                        # Simple heuristic to find company names
                        lines = text.split('\n')
                        for i, line in enumerate(lines):
                            if phone in line and i > 0:
                                potential_name = lines[i-1].strip()
                                if len(potential_name) > 5 and len(potential_name) < 50:
                                    buyers.append({
                                        'company_name': potential_name,
                                        'phone': phone,
                                        'email': emails[0] if emails else '',
                                        'website': directory_url,
                                        'business_type': 'Industry Directory',
                                        'confidence_score': 0.6,
                                        'source_url': directory_url
                                    })
                                    break
                
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.warning(f"Error scraping directory {directory_url}: {e}")
                
        return buyers
    
    def save_buyers(self, buyers):
        """Save buyers to database with deduplication"""
        if not buyers:
            return 0
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for buyer in buyers:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO buyers 
                    (company_name, phone, address, email, website, business_type, 
                     city, confidence_score, source_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    buyer.get('company_name', ''),
                    buyer.get('phone', ''),
                    buyer.get('address', ''),
                    buyer.get('email', ''),
                    buyer.get('website', ''),
                    buyer.get('business_type', ''),
                    buyer.get('city', ''),
                    buyer.get('confidence_score', 0.5),
                    buyer.get('source_url', '')
                ))
                
                if cursor.rowcount > 0:
                    saved_count += 1
                    
            except sqlite3.Error as e:
                logger.warning(f"Error saving buyer: {e}")
        
        conn.commit()
        conn.close()
        
        return saved_count
    
    def find_buyers(self):
        """Main method to find battery buyers"""
        logger.info("Starting battery buyer search...")
        
        all_buyers = []
        
        # Rotate through cities and search terms
        city = self.cities[self.current_city_index]
        search_term = self.search_terms[self.current_term_index]
        
        logger.info(f"Searching for '{search_term}' in {city}")
        
        # Try multiple scraping methods
        try:
            # Method 1: Yellow Pages
            yp_buyers = self.scrape_yellowpages(search_term, city)
            all_buyers.extend(yp_buyers)
            logger.info(f"Found {len(yp_buyers)} buyers from Yellow Pages")
            
            # Method 2: Google Business (if we need more)
            if len(all_buyers) < 5:
                gb_buyers = self.scrape_google_business(search_term, city)
                all_buyers.extend(gb_buyers)
                logger.info(f"Found {len(gb_buyers)} buyers from Google Business")
            
            # Method 3: Industry directories (if we still need more)
            if len(all_buyers) < 5:
                id_buyers = self.scrape_industry_directories(search_term)
                all_buyers.extend(id_buyers)
                logger.info(f"Found {len(id_buyers)} buyers from industry directories")
            
            # Method 4: Alternative scrapers (if we still need more)
            if len(all_buyers) < 5:
                # Try Craigslist
                cl_buyers = self.alt_scrapers.scrape_craigslist_services()
                all_buyers.extend(cl_buyers)
                logger.info(f"Found {len(cl_buyers)} buyers from Craigslist")
                
                # Try recycling centers
                if len(all_buyers) < 5:
                    rc_buyers = self.alt_scrapers.scrape_recycling_centers()
                    all_buyers.extend(rc_buyers)
                    logger.info(f"Found {len(rc_buyers)} buyers from recycling centers")
                
                # Try scrap yards
                if len(all_buyers) < 5:
                    sy_buyers = self.alt_scrapers.scrape_metal_scrap_yards()
                    all_buyers.extend(sy_buyers)
                    logger.info(f"Found {len(sy_buyers)} buyers from scrap yards")
                
        except Exception as e:
            logger.error(f"Error during buyer search: {e}")
        
        # Save results
        saved_count = self.save_buyers(all_buyers)
        logger.info(f"Saved {saved_count} new buyers to database")
        
        # Update rotation indices
        self.current_city_index = (self.current_city_index + 1) % len(self.cities)
        self.current_term_index = (self.current_term_index + 1) % len(self.search_terms)
        
        return saved_count
    
    def get_recent_buyers(self, hours=24):
        """Get buyers discovered in the last N hours"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM buyers 
            WHERE discovered_at > datetime('now', '-{} hours')
            ORDER BY discovered_at DESC
        '''.format(hours)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')
    
    def get_all_buyers(self):
        """Get all buyers from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM buyers ORDER BY discovered_at DESC', conn)
        conn.close()
        return df.to_dict('records')

# Flask web interface
app = Flask(__name__)
agent = BatteryBuyerAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/buyers')
def api_buyers():
    buyers = agent.get_all_buyers()
    return jsonify(buyers)

@app.route('/api/recent')
def api_recent():
    hours = request.args.get('hours', 24, type=int)
    buyers = agent.get_recent_buyers(hours)
    return jsonify(buyers)

@app.route('/api/stats')
def api_stats():
    conn = sqlite3.connect(agent.db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM buyers')
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM buyers WHERE discovered_at > datetime('now', '-24 hours')")
    last_24h = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM buyers WHERE discovered_at > datetime('now', '-1 hour')")
    last_hour = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_buyers': total,
        'last_24_hours': last_24h,
        'last_hour': last_hour
    })

def run_scheduled_search():
    """Run the scheduled buyer search"""
    try:
        agent.find_buyers()
    except Exception as e:
        logger.error(f"Scheduled search failed: {e}")

def main():
    """Main function to start the agent"""
    logger.info("Starting Battery Buyer Finder Agent...")
    
    # Schedule the search to run every hour
    schedule.every().hour.do(run_scheduled_search)
    
    # Run initial search
    logger.info("Running initial buyer search...")
    agent.find_buyers()
    
    # Start the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Flask web interface
    logger.info("Starting web interface on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == "__main__":
    main()