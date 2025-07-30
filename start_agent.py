#!/usr/bin/env python3
"""
Startup script for the Battery Buyer Finder Agent
"""

import sys
import os
import subprocess
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import requests
        import beautifulsoup4
        import selenium
        import schedule
        import pandas
        import fake_useragent
        import flask
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False

def main():
    """Main startup function"""
    print("🔋 Battery Buyer Finder Agent - Starting Up")
    print("=" * 50)
    
    # Check if dependencies are installed
    if not check_dependencies():
        print("\nAttempting to install dependencies...")
        if not install_dependencies():
            print("Please install dependencies manually: pip install -r requirements.txt")
            sys.exit(1)
    
    # Import and start the agent
    try:
        from battery_buyer_agent import main as agent_main
        print("\n🚀 Starting Battery Buyer Finder Agent...")
        print("📊 Web interface will be available at: http://localhost:5000")
        print("📝 Logs will be saved to: battery_buyer_agent.log")
        print("💾 Database will be created as: battery_buyers.db")
        print("\nPress Ctrl+C to stop the agent")
        print("=" * 50)
        
        agent_main()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()