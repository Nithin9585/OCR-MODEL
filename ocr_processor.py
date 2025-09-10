import easyocr
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile

# Memory optimization settings
MAX_IMAGE_SIZE = (2048, 2048)  # Limit image size to reduce memory usage

# Initialize EasyOCR reader cache
readers = {}

def process_document(file_path, languages=None):
    global readers
    if not languages:
        languages = ['en']

    lang_key = tuple(languages)
    if lang_key not in readers:
        # Use minimal memory settings for EasyOCR
        readers[lang_key] = easyocr.Reader(
            languages, 
            gpu=False,
            download_enabled=True,
            detector=True,
            recognizer=True,
            verbose=False,
            quantize=True  # Use quantized models to save memory
        )

    reader = readers[lang_key]
    all_results = {"pages": []}

    # Check if the file is a PDF
    if file_path.lower().endswith('.pdf'):
        # Convert PDF pages to a list of PIL Image objects
        images = convert_from_path(file_path)
        
        for i, pil_image in enumerate(images):
            # Create a temporary file for each image page
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_img:
                pil_image.save(tmp_img.name, 'PNG')
                temp_img_path = tmp_img.name
            
            try:
                # Process the temporary image file with EasyOCR
                results = reader.readtext(temp_img_path, detail=1)
                page_data = {"page_number": i + 1, "blocks": []}

                for bbox, text, confidence in results:
                    block = {
                        "text": text,
                        "confidence": float(confidence),
                        "position": {
                            "top_left": [float(c) for c in bbox[0]],
                            "top_right": [float(c) for c in bbox[1]],
                            "bottom_right": [float(c) for c in bbox[2]],
                            "bottom_left": [float(c) for c in bbox[3]]
                        }
                    }
                    page_data["blocks"].append(block)
                
                all_results["pages"].append(page_data)
            finally:
                # Clean up the temporary image file
                os.remove(temp_img_path)
    else:
        # If it's not a PDF, process it as a regular image
        # Optimize image size to reduce memory usage
        try:
            img = Image.open(file_path)
            if img.size[0] > MAX_IMAGE_SIZE[0] or img.size[1] > MAX_IMAGE_SIZE[1]:
                img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
                    img.save(tmp_img.name, 'JPEG', quality=85)
                    optimized_path = tmp_img.name
                results = reader.readtext(optimized_path, detail=1)
                os.remove(optimized_path)  # Clean up
            else:
                results = reader.readtext(file_path, detail=1)
        except Exception as e:
            # Fallback to original processing
            results = reader.readtext(file_path, detail=1)
        page_data = {"page_number": 1, "blocks": []}

        for bbox, text, confidence in results:
            block = {
                "text": text,
                "confidence": float(confidence),
                "position": {
                    "top_left": [float(c) for c in bbox[0]],
                    "top_right": [float(c) for c in bbox[1]],
                    "bottom_right": [float(c) for c in bbox[2]],
                    "bottom_left": [float(c) for c in bbox[3]]
                }
            }
            page_data["blocks"].append(block)
        
        all_results["pages"].append(page_data)

    return all_results