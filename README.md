# Scrap Battery Buyer Finder Agent

A novel autonomous agent that finds scrap battery buyers without requiring APIs. The agent scrapes publicly available information from multiple sources to identify potential buyers every hour.

## Features

- **API-Free Operation**: Uses web scraping instead of paid APIs
- **Automated Discovery**: Finds 5 new battery buyers every hour
- **Multiple Sources**: Scrapes from various websites including:
  - Yellow Pages directories
  - Business listings
  - Recycling company websites
  - Classified ad sites
  - Industry directories
- **Smart Deduplication**: Prevents duplicate entries
- **Data Persistence**: Stores findings in SQLite database
- **Web Interface**: Simple web UI to view discovered buyers
- **Scheduling**: Runs automatically every hour

## Quick Start

### Option 1: Easy Startup (Recommended)
```bash
python start_agent.py
```
This script will automatically install dependencies and start the agent.

### Option 2: Manual Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the agent:
```bash
python battery_buyer_agent.py
```

3. Access the web interface at `http://localhost:5000`

### Option 3: Test First
```bash
python test_agent.py
```
Run a quick test to verify everything works before starting the full agent.

## Usage

Once running, the agent will:
- Automatically search for battery buyers every hour
- Store results in a SQLite database (`battery_buyers.db`)
- Provide a web interface at `http://localhost:5000`
- Log all activities to `battery_buyer_agent.log`

### Web Interface Features
- **Dashboard**: Real-time statistics and recent discoveries
- **View All Buyers**: Complete database of discovered buyers
- **Filter by Time**: View buyers found in last hour or 24 hours
- **Auto-refresh**: Updates automatically every minute
- **Export**: Data can be accessed via JSON API endpoints

### API Endpoints
- `/api/buyers` - Get all discovered buyers
- `/api/recent?hours=24` - Get buyers from last N hours
- `/api/stats` - Get discovery statistics

## How It Works

The agent uses multiple scraping strategies:
1. **Directory Scraping**: Searches business directories for battery recyclers
2. **Geographic Targeting**: Rotates through different cities/regions
3. **Keyword Variation**: Uses different search terms to find buyers
4. **Smart Parsing**: Extracts contact information and business details
5. **Quality Filtering**: Validates and scores potential buyers

## Output

Each discovered buyer includes:
- Company name
- Phone number
- Address
- Email (when available)
- Website
- Business type
- Discovery timestamp
- Confidence score

## Configuration

The agent can be customized by editing `config.py`:
- Search terms and target cities
- Rate limiting and delays
- Confidence scoring
- Database settings
- Web interface options

## Files Created

- `battery_buyers.db` - SQLite database with discovered buyers
- `battery_buyer_agent.log` - Detailed activity logs
- `templates/` - Web interface templates

## Troubleshooting

### Common Issues
1. **ChromeDriver errors**: The agent will auto-download ChromeDriver
2. **Permission errors**: Run with appropriate permissions
3. **Network timeouts**: Agent includes retry logic and rate limiting
4. **No results found**: Try different search terms or cities in config

### Getting Help
- Check the log file for detailed error messages
- Run the test script to verify functionality
- Ensure all dependencies are properly installed

## Performance

- Targets 5 new buyers per hour as requested
- Uses intelligent deduplication to avoid repeats
- Rotates through cities and search terms for variety
- Implements respectful rate limiting
- Memory efficient with SQLite storage

## Legal & Ethical Considerations

- Scrapes only publicly available information
- Respects robots.txt and implements rate limiting
- Does not require API keys or paid services
- Follows best practices for web scraping
- Intended for legitimate business use only

## Future Enhancements

Potential improvements:
- Geographic expansion beyond US cities
- Additional data sources and directories
- Enhanced contact information validation
- Export functionality (CSV, Excel)
- Email verification features
- Integration with CRM systems