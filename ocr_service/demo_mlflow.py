#!/usr/bin/env python3
"""
MLflow OCR Tracking Demonstration Script

This script demonstrates the MLflow tracking capabilities for OCR operations.
It generates sample data and shows how to view metrics and performance data.
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_demo_images():
    """Create sample images for OCR testing."""
    demo_dir = Path("demo_images")
    demo_dir.mkdir(exist_ok=True)
    
    # Sample texts with different quality levels
    samples = [
        ("high_quality.png", "This is high quality text", (255, 255, 255), (0, 0, 0)),
        ("medium_quality.png", "Medium quality text sample", (240, 240, 240), (50, 50, 50)),
        ("low_quality.png", "Low quality blurry text", (200, 200, 200), (100, 100, 100)),
        ("mixed_quality.png", "Mixed Quality Document\nSome clear text\nSome unclear text", (255, 255, 255), (0, 0, 0))
    ]
    
    created_files = []
    
    for filename, text, bg_color, text_color in samples:
        filepath = demo_dir / filename
        
        # Create image
        img = Image.new('RGB', (400, 200), bg_color)
        draw = ImageDraw.Draw(img)
        
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text
        draw.text((20, 50), text, fill=text_color, font=font)
        
        # Save image
        img.save(filepath)
        created_files.append(filepath)
        print(f"✅ Created demo image: {filepath}")
    
    return created_files

def start_mlflow_server():
    """Start MLflow tracking server."""
    print("🚀 Starting MLflow tracking server...")
    
    # Set MLflow tracking URI
    os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5000"
    
    # Start MLflow server in background
    try:
        process = subprocess.Popen([
            sys.executable, "-m", "mlflow", "server",
            "--host", "0.0.0.0",
            "--port", "5000",
            "--backend-store-uri", "file:./mlruns",
            "--default-artifact-root", "./mlruns"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:5000/health")
            if response.status_code == 200:
                print("✅ MLflow server started successfully!")
                print("🌐 MLflow UI available at: http://localhost:5000")
                return process
            else:
                print("❌ MLflow server health check failed")
                return None
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to MLflow server")
            return None
            
    except Exception as e:
        print(f"❌ Failed to start MLflow server: {e}")
        return None

def test_ocr_with_mlflow(image_files):
    """Test OCR service with MLflow tracking."""
    print("\n📊 Testing OCR service with MLflow tracking...")
    
    ocr_url = "http://localhost:8002/extract"
    
    for image_file in image_files:
        print(f"\n🔍 Processing: {image_file.name}")
        
        # Test with different confidence thresholds
        confidence_levels = [0.0, 50.0, 70.0, 90.0]
        
        for confidence in confidence_levels:
            try:
                with open(image_file, 'rb') as f:
                    files = {'file': (image_file.name, f, 'image/png')}
                    params = {'min_confidence': confidence}
                    
                    response = requests.post(ocr_url, files=files, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"  ✅ Confidence {confidence}%: {data['filtered_word_count']}/{data['word_count']} words retained")
                    else:
                        print(f"  ❌ Error with confidence {confidence}%: {response.status_code}")
                        
            except Exception as e:
                print(f"  ❌ Failed to process {image_file.name} with confidence {confidence}%: {e}")
            
            # Small delay between requests
            time.sleep(0.5)

def generate_demo_commands():
    """Generate demonstration commands for stakeholders."""
    commands = """
# MLflow OCR Tracking Demonstration Commands
# ==========================================

# 1. Start MLflow Server
python -m mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri file:./mlruns

# 2. Access MLflow Web Interface
# Open browser to: http://localhost:5000

# 3. Start OCR Service (if not already running)
docker compose up -d ocr-service

# 4. Test OCR with different confidence levels
curl -X POST "http://localhost:8002/extract?min_confidence=0" \\
  -F "file=@demo_images/high_quality.png"

curl -X POST "http://localhost:8002/extract?min_confidence=70" \\
  -F "file=@demo_images/medium_quality.png"

curl -X POST "http://localhost:8002/extract?min_confidence=90" \\
  -F "file=@demo_images/low_quality.png"

# 5. View Results in MLflow UI
# - Navigate to http://localhost:5000
# - Click on "ocr_service_tracking" experiment
# - View individual runs and metrics
# - Compare confidence scores and processing times

# Key Metrics to Show Stakeholders:
# ================================
# - Average confidence scores per document type
# - Processing time trends
# - Word filtering effectiveness
# - Error rates and types
# - File size vs processing time correlation
# - Confidence threshold optimization insights
"""
    
    with open("mlflow_demo_commands.txt", "w") as f:
        f.write(commands)
    
    print("📝 Demo commands saved to: mlflow_demo_commands.txt")

def main():
    """Main demonstration function."""
    print("🎯 MLflow OCR Tracking Demonstration")
    print("=" * 50)
    
    # Step 1: Create demo images
    print("\n📸 Step 1: Creating demo images...")
    image_files = create_demo_images()
    
    # Step 2: Generate demo commands
    print("\n📝 Step 2: Generating demo commands...")
    generate_demo_commands()
    
    # Step 3: Start MLflow server
    print("\n🚀 Step 3: Starting MLflow server...")
    mlflow_process = start_mlflow_server()
    
    if mlflow_process:
        print("\n✅ MLflow server is running!")
        print("\n🎯 Next Steps for Demonstration:")
        print("1. Open browser to: http://localhost:5000")
        print("2. Ensure OCR service is running: docker compose up -d ocr-service")
        print("3. Run the test commands from mlflow_demo_commands.txt")
        print("4. View results in MLflow UI")
        
        # Step 4: Test OCR if service is available
        try:
            response = requests.get("http://localhost:8002/health")
            if response.status_code == 200:
                print("\n🔍 OCR service detected! Running automated tests...")
                test_ocr_with_mlflow(image_files)
            else:
                print("\n⚠️  OCR service not available. Start it with: docker compose up -d ocr-service")
        except:
            print("\n⚠️  OCR service not available. Start it with: docker compose up -d ocr-service")
        
        print("\n🎉 Demonstration setup complete!")
        print("Press Ctrl+C to stop MLflow server when done.")
        
        try:
            mlflow_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping MLflow server...")
            mlflow_process.terminate()
            mlflow_process.wait()
            print("✅ MLflow server stopped.")
    
    else:
        print("\n❌ Failed to start MLflow server. Please check the setup.")

if __name__ == "__main__":
    main()
