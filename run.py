"""
Script to run the application.
"""
import subprocess
import time
import sys

def check_docker():
    """Check if Docker is installed and running."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker or Docker Compose is not installed or not running.")
        return False

def start_application():
    """Start the application using Docker Compose."""
    print("Starting the application...")

    # Build and start the containers
    try:
        subprocess.run(["docker-compose", "build"], check=True)
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Application started successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start the application: {e}")
        return False

def wait_for_services():
    """Wait for all services to be ready."""
    print("Waiting for services to be ready...")

    # Wait for a maximum of 2 minutes
    max_wait_time = 120
    start_time = time.time()

    services = [
        {"name": "OCR Service", "url": "http://localhost:8000/"},
        {"name": "LLM Service", "url": "http://localhost:8001/health"},
        {"name": "Backend Service", "url": "http://localhost:8002/health"},
        {"name": "Frontend Service", "url": "http://localhost:8080"}
    ]

    import requests

    while time.time() - start_time < max_wait_time:
        all_ready = True

        for service in services:
            try:
                response = requests.get(service["url"], timeout=1)
                if response.status_code == 200:
                    service["ready"] = True
                else:
                    service["ready"] = False
                    all_ready = False
            except requests.exceptions.RequestException:
                service["ready"] = False
                all_ready = False

        if all_ready:
            print("✅ All services are ready.")
            return True

        # Print status
        for service in services:
            status = "✅" if service.get("ready", False) else "❌"
            print(f"{status} {service['name']}")

        print(f"Waiting for services... ({int(time.time() - start_time)}s)")
        time.sleep(5)

    print("❌ Timed out waiting for services.")
    return False

def run_tests():
    """Run the tests."""
    print("Running tests...")

    try:
        subprocess.run([sys.executable, "test_app.py"], check=True)
        print("✅ Tests passed.")
        return True
    except subprocess.CalledProcessError:
        print("❌ Tests failed.")
        return False

def main():
    """Run the application."""
    if not check_docker():
        sys.exit(1)

    if not start_application():
        sys.exit(1)

    if not wait_for_services():
        print("Services are not ready. You may need to check the logs:")
        print("docker-compose logs")
        sys.exit(1)

    if not run_tests():
        sys.exit(1)

    print("\n✅ Application is running successfully!")
    print("You can access the application at http://localhost:8080")
    print("\nTo stop the application, run:")
    print("docker-compose down")

if __name__ == "__main__":
    main()
