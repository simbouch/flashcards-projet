"""
Test script to verify that the application works.
"""
import requests
import time
import sys

def test_ocr_service():
    """Test the OCR service."""
    print("Testing OCR service...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ OCR service is running")
            return True
        else:
            print("❌ OCR service is not running correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ OCR service is not running")
        return False

def test_llm_service():
    """Test the LLM service."""
    print("Testing LLM service...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ LLM service is running")
            return True
        else:
            print("❌ LLM service is not running correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ LLM service is not running")
        return False

def test_backend_service():
    """Test the backend service."""
    print("Testing backend service...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ Backend service is running")
            return True
        else:
            print("❌ Backend service is not running correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        return False

def test_frontend_service():
    """Test the frontend service."""
    print("Testing frontend service...")
    try:
        response = requests.get("http://localhost:8080")
        if response.status_code == 200:
            print("✅ Frontend service is running")
            return True
        else:
            print("❌ Frontend service is not running correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend service is not running")
        return False

def test_user_registration():
    """Test user registration."""
    print("Testing user registration...")
    try:
        response = requests.post(
            "http://localhost:8002/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "Password123",
                "full_name": "Test User"
            }
        )
        if response.status_code == 200:
            print("✅ User registration works")
            return True
        else:
            print(f"❌ User registration failed: {response.json()}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        return False

def test_user_login():
    """Test user login."""
    print("Testing user login...")
    try:
        # Create form data for login
        data = {
            "username": "testuser",
            "password": "Password123"
        }
        response = requests.post(
            "http://localhost:8002/api/v1/auth/login",
            data=data
        )
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ User login works")
            return response.json()["access_token"]
        else:
            print(f"❌ User login failed: {response.json()}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        return None

def main():
    """Run all tests."""
    print("Starting tests...")
    
    # Test services
    ocr_ok = test_ocr_service()
    llm_ok = test_llm_service()
    backend_ok = test_backend_service()
    frontend_ok = test_frontend_service()
    
    if not (ocr_ok and llm_ok and backend_ok and frontend_ok):
        print("\n❌ Some services are not running. Please check the logs.")
        sys.exit(1)
    
    # Test user registration and login
    registration_ok = test_user_registration()
    
    if not registration_ok:
        print("\n❌ User registration failed. Please check the logs.")
        sys.exit(1)
    
    # Wait a bit for the database to update
    time.sleep(1)
    
    token = test_user_login()
    
    if not token:
        print("\n❌ User login failed. Please check the logs.")
        sys.exit(1)
    
    print("\n✅ All tests passed! The application is working correctly.")

if __name__ == "__main__":
    main()
