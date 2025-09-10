import easyocr
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import gc
import logging
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)

# Memory optimization settings
MAX_IMAGE_SIZE = (1536, 1536)  # Reduced image size for better memory usage
MAX_PDF_PAGES = 20  # Limit PDF pages to process
JPEG_QUALITY = 85  # Quality for image compression

# Initialize EasyOCR reader cache (limit to prevent memory issues)
readers = {}
MAX_READERS = 3  # Limit number of cached readers

def get_or_create_reader(languages):
    """Get cached reader or create new one with memory optimization"""
    global readers
    
    lang_key = tuple(sorted(languages))
    
    # If we have too many readers, clear the cache
    if len(readers) >= MAX_READERS:
        logger.info(f"Clearing reader cache (had {len(readers)} readers)")
        readers.clear()
        gc.collect()
    
    if lang_key not in readers:
        logger.info(f"Creating new EasyOCR reader for languages: {languages}")
        try:
            # Use minimal memory settings for EasyOCR
            reader = easyocr.Reader(
                languages, 
                gpu=False,
                download_enabled=True,
                detector=True,
                recognizer=True,
                verbose=False,
                quantize=True,  # Use quantized models to save memory
                model_storage_directory=None  # Use default model storage
            )
            readers[lang_key] = reader
            logger.info(f"Successfully created reader for {languages}")
        except Exception as e:
            logger.error(f"Failed to create EasyOCR reader: {e}")
            # Fallback to English only
            if languages != ['en']:
                logger.info("Falling back to English-only reader")
                return get_or_create_reader(['en'])
            raise
    
    return readers[lang_key]

def optimize_image(image_path, max_size=MAX_IMAGE_SIZE, quality=JPEG_QUALITY):
    """Optimize image for OCR processing"""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            original_size = img.size
            logger.debug(f"Original image size: {original_size}")
            
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {img.size}")
            
            # Save optimized version
            optimized_path = f"{image_path}_optimized.jpg"
            img.save(optimized_path, 'JPEG', quality=quality, optimize=True)
            logger.debug(f"Saved optimized image to: {optimized_path}")
            
            return optimized_path
    except Exception as e:
        logger.error(f"Image optimization failed: {e}")
        return image_path  # Return original if optimization fails

def process_document(file_path, languages=None):
    """Process document with improved error handling and memory management"""
    if not languages:
        languages = ['en']
    
    logger.info(f"Processing document: {file_path} with languages: {languages}")
    
    try:
        reader = get_or_create_reader(languages)
    except Exception as e:
        logger.error(f"Failed to get OCR reader: {e}")
        raise Exception(f"OCR reader initialization failed: {str(e)}")
    
    all_results = {"pages": []}
    temp_files = []  # Track temp files for cleanup
    try:
        # Check if the file is a PDF
        if file_path.lower().endswith('.pdf'):
            logger.info("Processing PDF document")
            try:
                # Convert PDF pages to a list of PIL Image objects
                images = convert_from_path(file_path, dpi=200, first_page=1, last_page=MAX_PDF_PAGES)
                logger.info(f"PDF converted to {len(images)} images")
                
                for i, pil_image in enumerate(images):
                    logger.debug(f"Processing PDF page {i+1}")
                    
                    # Create a temporary file for each image page
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
                        # Optimize the image before saving
                        if pil_image.size[0] > MAX_IMAGE_SIZE[0] or pil_image.size[1] > MAX_IMAGE_SIZE[1]:
                            pil_image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                            
                        pil_image.save(tmp_img.name, 'JPEG', quality=JPEG_QUALITY)
                        temp_img_path = tmp_img.name
                        temp_files.append(temp_img_path)
                    
                    try:
                        # Process the temporary image file with EasyOCR
                        results = reader.readtext(temp_img_path, detail=1)
                        page_data = {"page_number": i + 1, "blocks": []}

                        for bbox, text, confidence in results:
                            if confidence > 0.1:  # Filter out low confidence results
                                block = {
                                    "text": text.strip(),
                                    "confidence": round(float(confidence), 3),
                                    "position": {
                                        "top_left": [round(float(c), 2) for c in bbox[0]],
                                        "top_right": [round(float(c), 2) for c in bbox[1]],
                                        "bottom_right": [round(float(c), 2) for c in bbox[2]],
                                        "bottom_left": [round(float(c), 2) for c in bbox[3]]
                                    }
                                }
                                page_data["blocks"].append(block)
                        
                        all_results["pages"].append(page_data)
                        logger.debug(f"Page {i+1} processed: {len(page_data['blocks'])} blocks found")
                        
                    except Exception as e:
                        logger.error(f"Error processing PDF page {i+1}: {e}")
                        # Continue with next page instead of failing completely
                        
            except Exception as e:
                logger.error(f"PDF processing failed: {e}")
                raise Exception(f"PDF processing failed: {str(e)}")
        else:
            # If it's not a PDF, process it as a regular image
            logger.info("Processing regular image")
            
            try:
                # Optimize the image first
                optimized_path = optimize_image(file_path)
                temp_files.append(optimized_path)
                
                # Process with EasyOCR
                results = reader.readtext(optimized_path, detail=1)
                page_data = {"page_number": 1, "blocks": []}

                for bbox, text, confidence in results:
                    if confidence > 0.1:  # Filter out low confidence results
                        block = {
                            "text": text.strip(),
                            "confidence": round(float(confidence), 3),
                            "position": {
                                "top_left": [round(float(c), 2) for c in bbox[0]],
                                "top_right": [round(float(c), 2) for c in bbox[1]],
                                "bottom_right": [round(float(c), 2) for c in bbox[2]],
                                "bottom_left": [round(float(c), 2) for c in bbox[3]]
                            }
                        }
                        page_data["blocks"].append(block)
                
                all_results["pages"].append(page_data)
                logger.info(f"Image processed: {len(page_data['blocks'])} blocks found")
                
            except Exception as e:
                logger.error(f"Image processing failed: {e}")
                raise Exception(f"Image processing failed: {str(e)}")
                
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {temp_file}: {e}")
        
        # Force garbage collection
        gc.collect()

    logger.info(f"Document processing completed: {len(all_results['pages'])} pages processed")
    return all_results