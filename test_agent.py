#!/usr/bin/env python3
"""
Test script for the Battery Buyer Finder Agent
"""

import sqlite3
import time
from battery_buyer_agent import BatteryBuyerAgent

def test_agent():
    """Test the basic functionality of the agent"""
    print("🧪 Testing Battery Buyer Finder Agent")
    print("=" * 40)
    
    # Initialize agent
    agent = BatteryBuyerAgent()
    print("✓ Agent initialized successfully")
    
    # Test database connection
    try:
        conn = sqlite3.connect(agent.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM buyers")
        initial_count = cursor.fetchone()[0]
        conn.close()
        print(f"✓ Database connected. Initial buyer count: {initial_count}")
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False
    
    # Test finding buyers (limited run)
    print("\n🔍 Testing buyer search (this may take a minute)...")
    try:
        # Run a limited search
        saved_count = agent.find_buyers()
        print(f"✓ Search completed. New buyers found: {saved_count}")
    except Exception as e:
        print(f"✗ Search error: {e}")
        return False
    
    # Test database retrieval
    try:
        all_buyers = agent.get_all_buyers()
        recent_buyers = agent.get_recent_buyers(24)
        print(f"✓ Database retrieval successful")
        print(f"   Total buyers: {len(all_buyers)}")
        print(f"   Recent buyers (24h): {len(recent_buyers)}")
        
        # Show sample data if available
        if all_buyers:
            print(f"\n📋 Sample buyer data:")
            sample = all_buyers[0]
            for key, value in sample.items():
                if key not in ['id']:
                    print(f"   {key}: {value}")
                    
    except Exception as e:
        print(f"✗ Database retrieval error: {e}")
        return False
    
    print("\n✅ All tests passed! Agent is ready to run.")
    print("\n💡 To start the full agent:")
    print("   python start_agent.py")
    print("   or")
    print("   python battery_buyer_agent.py")
    
    return True

if __name__ == "__main__":
    test_agent()