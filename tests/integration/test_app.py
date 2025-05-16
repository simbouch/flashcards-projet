"""
Test script to verify that the application works.
"""
import requests
import time
import sys

# Global variables to store test data
test_credentials = None
access_token = None

def test_ocr_service():
    """Test the OCR service."""
    print("Testing OCR service...")
    try:
        # Check if the Swagger docs are accessible, which indicates the service is running
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ OCR service is running")
            assert True
        else:
            print("❌ OCR service is not running correctly")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ OCR service is not running")
        assert False

def test_llm_service():
    """Test the LLM service."""
    print("Testing LLM service...")
    try:
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ LLM service is running")
            assert True
        else:
            print("❌ LLM service is not running correctly")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ LLM service is not running")
        assert False

def test_backend_service():
    """Test the backend service."""
    print("Testing backend service...")
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print("✅ Backend service is running")
            assert True
        else:
            print("❌ Backend service is not running correctly")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        assert False

def test_frontend_service():
    """Test the frontend service."""
    print("Testing frontend service...")
    try:
        response = requests.get("http://localhost:8080")
        if response.status_code == 200:
            print("✅ Frontend service is running")
            assert True
        else:
            print("❌ Frontend service is not running correctly")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend service is not running")
        assert False

def test_user_registration():
    """Test user registration."""
    print("Testing user registration...")
    try:
        # Generate a unique email to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        email = f"test{unique_id}@example.com"
        username = f"testuser{unique_id}"

        response = requests.post(
            "http://localhost:8002/api/v1/auth/register",
            json={
                "email": email,
                "username": username,
                "password": "Password123",
                "full_name": "Test User"
            }
        )
        if response.status_code == 200:
            print("✅ User registration works")
            # Save the credentials for login test
            global test_credentials
            test_credentials = {
                "username": username,
                "password": "Password123"
            }
            assert True
        else:
            print(f"❌ User registration failed: {response.json()}")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        assert False

def test_user_login():
    """Test user login."""
    print("Testing user login...")
    try:
        # Use the credentials from the registration test
        if not test_credentials:
            print("❌ No test credentials available. Registration test must run first.")
            assert False

        response = requests.post(
            "http://localhost:8002/api/v1/auth/login",
            data=test_credentials
        )
        if response.status_code == 200 and "access_token" in response.json():
            print("✅ User login works")
            # Store the token in a global variable for future tests
            global access_token
            access_token = response.json()["access_token"]
            assert True
        else:
            print(f"❌ User login failed: {response.json()}")
            assert False
    except requests.exceptions.ConnectionError:
        print("❌ Backend service is not running")
        assert False

def main():
    """Run all tests."""
    print("Starting tests...")

    try:
        # Test services
        test_ocr_service()
        test_llm_service()
        test_backend_service()
        test_frontend_service()

        # Test user registration and login
        test_user_registration()

        # Wait a bit for the database to update
        time.sleep(1)

        test_user_login()

        print("\n✅ All tests passed! The application is working correctly.")
    except AssertionError:
        print("\n❌ Some tests failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
