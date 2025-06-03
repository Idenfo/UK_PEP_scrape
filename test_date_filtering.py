#!/usr/bin/env python3
"""
Test script to validate all date-based filtering functionality.
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_endpoint(endpoint, description):
    """Test an endpoint and display results."""
    print(f"\n=== {description} ===")
    print(f"Testing: {endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if 'summary' in data and 'total_count' in data['summary']:
                count = data['summary']['total_count']
                print(f"✅ Success: {count} records")
            elif 'summary' in data:
                print(f"✅ Success: {json.dumps(data['summary'], indent=2)}")
            else:
                print(f"✅ Success: Response received")
            
            # Show metadata if available
            if 'metadata' in data:
                metadata = data['metadata']
                filters = []
                if metadata.get('filter_current'):
                    filters.append("current=true")
                if metadata.get('from_date'):
                    filters.append(f"from_date={metadata['from_date']}")
                if metadata.get('to_date'):
                    filters.append(f"to_date={metadata['to_date']}")
                if metadata.get('on_date'):
                    filters.append(f"on_date={metadata['on_date']}")
                
                if filters:
                    print(f"   Filters applied: {', '.join(filters)}")
                    
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_csv_export(endpoint, description):
    """Test a CSV export endpoint and display results."""
    print(f"\n=== {description} ===")
    print(f"Testing: POST {endpoint}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Success: {data['file_count']} files exported")
                print(f"   Files: {', '.join(data['exported_files'])}")
            else:
                print(f"❌ Failed: {data}")
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Run all tests."""
    print("🧪 Testing UK PEP Scraper Date Filtering Functionality")
    print("=" * 60)
    
    # Test current filtering
    test_endpoint("/scrape/mps", "All MPs (baseline)")
    test_endpoint("/scrape/mps?current=true", "Current MPs only")
    test_endpoint("/scrape/lords?current=true", "Current Lords only")
    
    # Test date filtering
    test_endpoint("/scrape/mps?from_date=2024-01-01", "MPs from 2024 onwards")
    test_endpoint("/scrape/lords?on_date=2024-06-01", "Lords on specific date")
    test_endpoint("/scrape/mps?from_date=2023-01-01&to_date=2023-12-31", "MPs in date range")
    
    # Test combined filtering
    test_endpoint("/scrape/mps?current=true&from_date=2024-01-01", "Current MPs from 2024")
    test_endpoint("/scrape/lords?current=true&on_date=2024-06-01", "Current Lords on date")
    
    # Test edge cases
    test_endpoint("/scrape/mps?from_date=2030-01-01", "MPs from future date")
    test_endpoint("/scrape/lords?on_date=1800-01-01", "Lords from historical date")
    
    # Test CSV exports
    test_csv_export("/export/csv?type=mps&current=true", "CSV: Current MPs")
    test_csv_export("/export/csv?type=lords&from_date=2024-01-01", "CSV: Lords from 2024")
    test_csv_export("/export/csv?type=mps&current=true&from_date=2024-01-01", "CSV: Current MPs from 2024")
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")

if __name__ == "__main__":
    main()
