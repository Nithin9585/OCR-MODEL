#!/usr/bin/env python3
"""
Quick test script for the OCR service
"""
import requests
import json
import time
import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_test_image(text="Hello World! OCR Test 123"):
    """Create a simple test image with text"""
    img = Image.new('RGB', (400, 100), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((10, 30), text, fill='black', font=font)
    
    test_image_path = "quick_test_image.png"
    img.save(test_image_path)
    print(f"✅ Created test image: {test_image_path}")
    return test_image_path

def test_ocr_service(base_url="http://localhost:5000"):
    """Test the OCR service comprehensively"""
    
    print(f"🧪 Testing OCR Service at {base_url}")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing health endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=10)
        elapsed = time.time() - start_time
        
        print(f"   Response time: {elapsed:.2f}s")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            health_data = response.json()
            print(f"   Service: {health_data.get('service')}")
            print(f"   Status: {health_data.get('status')}")
            print(f"   OCR Status: {health_data.get('ocr_status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Root endpoint
    print("\n2️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            root_data = response.json()
            print(f"   Available endpoints: {list(root_data.get('endpoints', {}).keys())}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: OCR endpoint
    print("\n3️⃣ Testing OCR endpoint...")
    
    # Create test image
    test_image_path = create_test_image()
    
    try:
        # Get file size
        file_size = os.path.getsize(test_image_path)
        print(f"   Test image size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        # Send OCR request
        print("   Sending OCR request...")
        start_time = time.time()
        
        with open(test_image_path, 'rb') as f:
            files = {'file': f}
            data = {'lang': 'en'}
            response = requests.post(
                f"{base_url}/ocr", 
                files=files, 
                data=data, 
                timeout=60  # 60 second timeout
            )
        
        elapsed = time.time() - start_time
        print(f"   Request completed in {elapsed:.2f} seconds")
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ OCR test passed")
            try:
                result = response.json()
                
                # Display results
                pages = result.get('pages', [])
                print(f"   Pages processed: {len(pages)}")
                
                if pages:
                    blocks = pages[0].get('blocks', [])
                    print(f"   Text blocks found: {len(blocks)}")
                    
                    for i, block in enumerate(blocks[:3]):  # Show first 3 blocks
                        text = block['text']
                        confidence = block['confidence']
                        print(f"     Block {i+1}: '{text}' (confidence: {confidence:.2f})")
                
                # Show processing info if available
                if 'processing_info' in result:
                    proc_info = result['processing_info']
                    print(f"   Processing time: {proc_info.get('processing_time_seconds', 'N/A')}s")
                    print(f"   Languages used: {proc_info.get('languages_used', 'N/A')}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"   Raw response: {response.text[:200]}...")
                
        else:
            print(f"❌ OCR test failed: {response.status_code}")
            print(f"   Error response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ OCR request timed out (>60s)")
    except Exception as e:
        print(f"❌ OCR test error: {e}")
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            print(f"   Cleaned up test image")
    
    print("\n🏁 Testing complete!")
    return True

def main():
    # Allow custom URL via command line
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"Testing OCR service at: {url}")
    
    success = test_ocr_service(url)
    
    if success:
        print("\n🎉 All basic tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the service logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
