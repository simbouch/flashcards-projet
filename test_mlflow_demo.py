#!/usr/bin/env python3
"""
Quick MLflow demonstration with correct OCR service port
"""

import requests
import time
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (300, 100), 'white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), "Hello MLflow Test", fill='black')
    
    test_file = Path("test_image.png")
    img.save(test_file)
    return test_file

def test_ocr_with_mlflow():
    """Test OCR service with MLflow tracking"""
    print("🔍 Testing OCR service with MLflow tracking...")
    
    # Create test image
    test_file = create_test_image()
    print(f"✅ Created test image: {test_file}")
    
    # Test different confidence levels
    confidence_levels = [0.0, 50.0, 70.0, 90.0]
    
    for confidence in confidence_levels:
        print(f"\n📊 Testing with confidence threshold: {confidence}%")
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file.name, f, 'image/png')}
                params = {'min_confidence': confidence}
                
                # Use correct port 8000
                response = requests.post('http://localhost:8000/extract', 
                                       files=files, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success!")
                    print(f"     Original text: '{data.get('text', '')}'")
                    print(f"     Filtered text: '{data.get('filtered_text', '')}'")
                    print(f"     Average confidence: {data.get('average_confidence', 0)}%")
                    print(f"     Words retained: {data.get('filtered_word_count', 0)}/{data.get('word_count', 0)}")
                    
                    if 'confidence_stats' in data:
                        stats = data['confidence_stats']
                        print(f"     High confidence words: {stats.get('high_confidence_count', 0)}")
                        print(f"     Words filtered out: {stats.get('words_filtered_out', 0)}")
                else:
                    print(f"  ❌ Error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        
        time.sleep(1)  # Small delay between requests

if __name__ == "__main__":
    print("🎯 MLflow OCR Tracking Quick Demo")
    print("=" * 40)
    print("🌐 MLflow UI: http://localhost:5000")
    print("🔧 OCR Service: http://localhost:8000")
    print()
    
    test_ocr_with_mlflow()
    
    print("\n🎉 Demo complete!")
    print("📊 Check MLflow UI at http://localhost:5000 to see the tracked operations")
    print("   - Click on 'ocr_service_tracking' experiment")
    print("   - View individual runs and their metrics")
    print("   - Compare confidence thresholds and their effectiveness")
