#!/usr/bin/env python3
"""
Test script to verify data synchronization between resume upload, profile, and opportunities
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "john.doe@example.com"

def test_profile_sync():
    """Test profile data retrieval"""
    print("🔍 Testing Profile Data Sync...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/consultant/{TEST_EMAIL}/profile")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile fetched successfully")
            print(f"   - Consultant: {data['consultant']['name']}")
            print(f"   - Skills: {data['total_skills']}")
            print(f"   - Resume Status: {data['consultant']['resume_status']}")
            if data.get('resume_data'):
                print(f"   - Has Resume: {data['resume_data']['has_resume']}")
                print(f"   - Last Upload: {data['resume_data']['last_upload']}")
            return True
        else:
            print(f"❌ Profile fetch failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile fetch error: {str(e)}")
        return False

def test_opportunities_sync():
    """Test opportunity recommendations"""
    print("\n🎯 Testing Opportunity Sync...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/consultant-opportunities/{TEST_EMAIL}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Opportunities fetched successfully")
            print(f"   - Recommended: {data['total_recommended']}")
            print(f"   - Applied: {data['total_applied']}")
            
            if data['recommended_opportunities']:
                top_match = data['recommended_opportunities'][0]
                print(f"   - Top Match: {top_match['opportunity']['title']} ({top_match['match_score']:.2f})")
            return True
        else:
            print(f"❌ Opportunities fetch failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Opportunities fetch error: {str(e)}")
        return False

def test_backend_health():
    """Test backend health"""
    print("🏥 Testing Backend Health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Data Synchronization Test\n")
    
    health_ok = test_backend_health()
    profile_ok = test_profile_sync()
    opportunities_ok = test_opportunities_sync()
    
    print(f"\n📊 Test Results:")
    print(f"   Backend Health: {'✅' if health_ok else '❌'}")
    print(f"   Profile Sync: {'✅' if profile_ok else '❌'}")
    print(f"   Opportunities Sync: {'✅' if opportunities_ok else '❌'}")
    
    if all([health_ok, profile_ok, opportunities_ok]):
        print("\n🎉 All systems are synchronized and working properly!")
    else:
        print("\n⚠️  Some issues detected. Check the backend logs for more details.")
