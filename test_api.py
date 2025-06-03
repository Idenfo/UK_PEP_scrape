#!/usr/bin/env python3
"""
Test script for the UK Government Members Scraper API
Demonstrates all available endpoints and their JSON responses
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_endpoint(endpoint, description):
    """Test an API endpoint and display results"""
    print(f"\n🌐 Testing: {endpoint}")
    print(f"📝 Description: {description}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            
            # Show summary information based on endpoint
            if endpoint == "/health":
                print(f"📊 Health Status: {data.get('status')}")
                print(f"🗄️  Cache Status: {data.get('cache_status')}")
            
            elif endpoint == "/scrape/mps":
                summary = data.get('summary', {})
                print(f"📊 Total MPs: {summary.get('total_count', 0)}")
                print(f"📅 Scraped at: {data.get('metadata', {}).get('scraped_at')}")
                
                # Show sample MP
                mps = data.get('members_of_parliament', [])
                if mps:
                    print(f"👤 Sample MP: {mps[0].get('display_name')} ({mps[0].get('full_title')})")
            
            elif endpoint == "/scrape/lords":
                summary = data.get('summary', {})
                print(f"📊 Total Lords: {summary.get('total_count', 0)}")
                print(f"📅 Scraped at: {data.get('metadata', {}).get('scraped_at')}")
                
                # Show sample Lord
                lords = data.get('house_of_lords', [])
                if lords:
                    print(f"👤 Sample Lord: {lords[0].get('display_name')} ({lords[0].get('full_title')})")
            
            elif endpoint == "/scrape/government-roles":
                summary = data.get('summary', {})
                print(f"📊 MPs with Government Roles: {summary.get('total_mps_government_roles', 0)}")
                print(f"📊 Lords with Government Roles: {summary.get('total_lords_government_roles', 0)}")
                
                # Show sample government role
                gov_roles = data.get('government_roles', {})
                mps_roles = gov_roles.get('mps_government_roles', [])
                if mps_roles:
                    role = mps_roles[0]
                    print(f"👤 Sample Gov Role: {role.get('display_name')} - {role.get('position_name')}")
            
            elif endpoint == "/scrape/committees":
                summary = data.get('summary', {})
                print(f"📊 MPs Committee Memberships: {summary.get('total_mps_committee_memberships', 0)}")
                print(f"📊 Lords Committee Memberships: {summary.get('total_lords_committee_memberships', 0)}")
            
            elif endpoint == "/scrape/all":
                summary = data.get('summary', {})
                print(f"📊 Complete Dataset Summary:")
                print(f"   • Total MPs: {summary.get('total_mps', 0)}")
                print(f"   • Total Lords: {summary.get('total_lords', 0)}")
                print(f"   • MPs with Government Roles: {summary.get('total_mps_gov_roles', 0)}")
                print(f"   • Lords with Government Roles: {summary.get('total_lords_gov_roles', 0)}")
                print(f"   • MPs Committee Memberships: {summary.get('total_mps_committee_memberships', 0)}")
                print(f"   • Lords Committee Memberships: {summary.get('total_lords_committee_memberships', 0)}")
                print(f"📅 Scraped at: {data.get('metadata', {}).get('scraped_at')}")
            
            elif endpoint == "/":
                print(f"📊 Service: {data.get('service')}")
                print(f"🔗 Available Endpoints: {len(data.get('endpoints', {}))}")
                for ep, desc in data.get('endpoints', {}).items():
                    print(f"   • {ep}: {desc}")
            
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_csv_export_endpoint(data_type="all"):
    """Test the CSV export endpoint"""
    print(f"\n🌐 Testing CSV Export: /export/csv?type={data_type}")
    print(f"📝 Description: Export {data_type} data to CSV files")
    
    try:
        response = requests.post(f"{BASE_URL}/export/csv?type={data_type}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Export Status: {data.get('status')}")
            print(f"📁 Files Exported: {data.get('files_exported', 0)}")
            
            # Show exported files
            files = data.get('files', [])
            if files:
                print(f"📄 Generated Files:")
                for file_info in files:
                    print(f"   • {file_info.get('filename')} ({file_info.get('records', 0)} records)")
            
            print(f"📅 Export Time: {data.get('export_time')}")
            
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Flask app is running on http://localhost:5001")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print_section("UK Government Members Scraper API Test")
    print("Testing all available endpoints...")
    
    # Test each endpoint
    endpoints = [
        ("/", "API Information and Service Status"),
        ("/health", "Health Check"),
        ("/scrape/mps", "Members of Parliament (House of Commons)"),
        ("/scrape/lords", "Members of House of Lords"),
        ("/scrape/government-roles", "Government Roles and Positions"),
        ("/scrape/committees", "Committee Memberships"),
        ("/scrape/all", "Complete Dataset (All Data)")
    ]
    
    # Test all basic endpoints
    for endpoint, description in endpoints:
        test_endpoint(endpoint, description)
    
    # Test CSV export endpoints
    test_csv_export_endpoint("all")
    test_csv_export_endpoint("mps") 
    test_csv_export_endpoint("lords")
    test_csv_export_endpoint("government-roles")
    test_csv_export_endpoint("committees")
    
    print_section("Test Complete")
    print("🎉 All endpoints tested successfully!")
    print("\nCURL Examples:")
    print("• Health check:        curl http://localhost:5001/health")
    print("• Get all MPs:         curl http://localhost:5001/scrape/mps")
    print("• Get all Lords:       curl http://localhost:5001/scrape/lords")
    print("• Get gov roles:       curl http://localhost:5001/scrape/government-roles")
    print("• Get committees:      curl http://localhost:5001/scrape/committees")
    print("• Get everything:      curl http://localhost:5001/scrape/all")
    print("• Cached data:         curl http://localhost:5001/scrape/all?cache=true")
    print("\nCSV Export Examples:")
    print("• Export all data:     curl -X POST http://localhost:5001/export/csv?type=all")
    print("• Export MPs data:     curl -X POST http://localhost:5001/export/csv?type=mps")
    print("• Export Lords data:   curl -X POST http://localhost:5001/export/csv?type=lords")
    print("• Export gov roles:    curl -X POST http://localhost:5001/export/csv?type=government-roles")
    print("• Export committees:   curl -X POST http://localhost:5001/export/csv?type=committees")
