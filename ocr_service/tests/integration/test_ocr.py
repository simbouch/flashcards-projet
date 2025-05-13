import requests
import json
import sys

def extract_text_from_image(image_path):
    """Extract text from an image using the OCR service."""
    url = "http://localhost:8000/extract"
    
    # Open the image file in binary mode
    with open(image_path, "rb") as f:
        # Create a multipart form with the image file
        files = {"file": (image_path, f, "image/png")}
        
        # Make the request
        response = requests.post(url, files=files)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            return result.get("text", "")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <image_path>")
        return
    
    image_path = sys.argv[1]
    text = extract_text_from_image(image_path)
    
    if text:
        print("Extracted Text:")
        print(text)
    else:
        print("Failed to extract text from the image.")

if __name__ == "__main__":
    main()
