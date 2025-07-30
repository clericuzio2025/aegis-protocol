#!/usr/bin/env python3
"""
Configuration settings for the Battery Buyer Finder Agent
"""

# Search configuration
SEARCH_TERMS = [
    "scrap battery buyers",
    "battery recycling companies",
    "lead battery scrap dealers",
    "automotive battery recyclers",
    "industrial battery buyers",
    "battery scrap yard",
    "lead acid battery recycling",
    "battery disposal services",
    "scrap metal battery buyers",
    "battery core buyers",
    "used battery dealers",
    "car battery recycling"
]

# Geographic targeting - major US cities
TARGET_CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin",
    "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "Detroit",
    "Memphis", "Boston", "Seattle", "Denver", "Nashville",
    "Portland", "Las Vegas", "Louisville", "Baltimore", "Milwaukee",
    "Oklahoma City", "Atlanta", "Miami", "Kansas City", "Tampa"
]

# Craigslist city codes for alternative scraping
CRAIGSLIST_CITIES = [
    "newyork", "losangeles", "chicago", "houston", "phoenix",
    "philadelphia", "sandiego", "dallas", "austin", "jacksonville",
    "fortworth", "columbus", "charlotte", "detroit", "memphis",
    "boston", "seattle", "denver", "nashville", "portland"
]

# Rate limiting settings (seconds)
RATE_LIMITS = {
    "between_requests": (2, 5),     # Random delay between individual requests
    "between_sources": (3, 7),      # Delay between different data sources
    "selenium_wait": (2, 4),        # Wait time for selenium operations
    "error_backoff": 10             # Backoff time after errors
}

# Scraping targets and confidence scores
SOURCE_CONFIDENCE = {
    "Google Business": 0.8,
    "Yellow Pages": 0.7,
    "Industry Directory": 0.6,
    "Business Directory": 0.6,
    "Recycling Center": 0.5,
    "Classified Ad": 0.4,
    "Scrap Metal Yard": 0.7
}

# Database settings
DATABASE_CONFIG = {
    "path": "battery_buyers.db",
    "backup_interval": 24,  # hours
    "cleanup_old_entries": False,  # Set to True to remove old entries
    "max_age_days": 365
}

# Web interface settings
WEB_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": False,
    "auto_refresh_interval": 60  # seconds
}

# Scheduling settings
SCHEDULE_CONFIG = {
    "search_interval": 1,  # hours
    "target_buyers_per_hour": 5,
    "max_concurrent_searches": 3
}

# User agent rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Keywords for filtering relevant results
BATTERY_KEYWORDS = [
    "battery", "batteries", "lead", "acid", "automotive", "car", "truck",
    "marine", "industrial", "UPS", "backup", "rechargeable", "scrap",
    "recycling", "disposal", "core", "exchange", "buy", "purchase",
    "dealer", "yard", "metal", "lead-acid"
]

# Contact info validation patterns
VALIDATION_PATTERNS = {
    "phone": r"^(\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "company_name_min_length": 3,
    "company_name_max_length": 100
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "battery_buyer_agent.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}