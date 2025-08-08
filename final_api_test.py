#!/usr/bin/env python3
"""
Final API Integration Test
Tests all endpoints on port 8000 to verify complete functionality
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def test_endpoint(method, url, data=None, description=""):
    """Test an API endpoint and return the result"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        status = "✅ PASS" if response.status_code < 400 else "❌ FAIL"
        print(f"{status} {method} {url} - {response.status_code} - {description}")
        
        if response.status_code >= 400:
            print(f"   Error: {response.text[:100]}")
        
        return response
    except Exception as e:
        print(f"❌ FAIL {method} {url} - Exception: {str(e)[:100]}")
        return None

def main():
    print("🧪 Final API Integration Test - Port 8000")
    print("=" * 50)
    
    # Test 1: Dashboard metrics
    test_endpoint("GET", f"{API_BASE_URL}/api/dashboard/metrics", description="Dashboard metrics")
    
    # Test 2: Consultants list
    response = test_endpoint("GET", f"{API_BASE_URL}/api/consultants", description="Consultants list")
    
    # Test 3: Opportunities list
    opportunities_response = test_endpoint("GET", f"{API_BASE_URL}/api/opportunities", description="Opportunities list")
    
    # Test 4: Create new opportunity
    new_opportunity = {
        "title": "API Test Opportunity",
        "description": "Testing API integration functionality",
        "client_name": "Test Client",
        "required_skills": ["Python", "FastAPI"],
        "experience_level": "mid",
        "project_duration": "3 months",
        "budget_range": "$50,000 - $75,000",
        "start_date": "2025-09-01",
        "end_date": "2025-12-01"
    }
    create_response = test_endpoint("POST", f"{API_BASE_URL}/api/opportunities", new_opportunity, "Create opportunity")
    
    # Test 5: Consultant dashboard (if we have consultant emails)
    if response and response.status_code == 200:
        consultants = response.json()
        if consultants:
            first_consultant_email = consultants[0]['email']
            test_endpoint("GET", f"{API_BASE_URL}/api/consultant/dashboard/{first_consultant_email}", description="Consultant dashboard")
    
    # Test 6: Update opportunity (if we created one)
    if create_response and create_response.status_code == 201:
        new_opportunity_data = create_response.json()
        opportunity_id = new_opportunity_data['id']
        
        update_data = {
            "title": "Updated API Test Opportunity",
            "description": "Updated testing API integration functionality",
            "client_name": "Updated Test Client",
            "required_skills": ["Python", "FastAPI", "PostgreSQL"],
            "experience_level": "senior",
            "project_duration": "4 months",
            "budget_range": "$60,000 - $85,000",
            "start_date": "2025-09-01",
            "end_date": "2025-12-01"
        }
        test_endpoint("PUT", f"{API_BASE_URL}/api/opportunities/{opportunity_id}", update_data, "Update opportunity")
        
        # Test 7: Delete opportunity
        test_endpoint("DELETE", f"{API_BASE_URL}/api/opportunities/{opportunity_id}", description="Delete opportunity")
    
    print("\n" + "=" * 50)
    print("🎉 API Integration Test Complete!")
    print("Backend running on: http://localhost:8000")
    print("Frontend running on: http://localhost:3000")
    print("API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
