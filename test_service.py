import requests
import json
import os

def test_ocr_service(base_url="http://localhost:5000"):
    """Test the OCR service endpoints"""
    
    print(f"🧪 Testing OCR Service at {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print()
    
    # Test 2: Root endpoint
    print("2️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    print()
    
    # Test 3: OCR endpoint with sample image (if available)
    print("3️⃣ Testing OCR endpoint...")
    
    # Create a simple test image if none exists
    test_image_path = "test_image.png"
    if not os.path.exists(test_image_path):
        print("   Creating test image...")
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple test image with text
            img = Image.new('RGB', (400, 100), color='white')
            draw = ImageDraw.Draw(img)
            
            try:
                # Try to use a default font
                font = ImageFont.load_default()
            except:
                font = None
            
            draw.text((10, 30), "Hello World! OCR Test 123", fill='black', font=font)
            img.save(test_image_path)
            print(f"   Created test image: {test_image_path}")
        except ImportError:
            print("   Pillow not available, skipping test image creation")
            return
    
    if os.path.exists(test_image_path):
        try:
            with open(test_image_path, 'rb') as f:
                files = {'file': f}
                data = {'lang': 'en'}
                response = requests.post(f"{base_url}/ocr", files=files, data=data)
            
            if response.status_code == 200:
                print("✅ OCR test passed")
                result = response.json()
                print(f"   Pages found: {len(result.get('pages', []))}")
                if result.get('pages'):
                    blocks = result['pages'][0].get('blocks', [])
                    print(f"   Text blocks found: {len(blocks)}")
                    for i, block in enumerate(blocks[:3]):  # Show first 3 blocks
                        print(f"     Block {i+1}: '{block['text']}' (confidence: {block['confidence']:.2f})")
            else:
                print(f"❌ OCR test failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ OCR test error: {e}")
    else:
        print("   No test image available, skipping OCR test")
    
    print()
    print("🏁 Testing complete!")

if __name__ == "__main__":
    import sys
    
    # Allow custom URL via command line
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_ocr_service(url)
