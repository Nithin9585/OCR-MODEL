import os
import tempfile
import time
import gc
from flask import Flask, request, jsonify
from ocr_processor import process_document
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure for production
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


def allowed_file(filename):
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
    return os.path.splitext(filename)[1].lower() in allowed_extensions

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Railway"""
    try:
        # Import here to avoid startup issues
        from ocr_processor import get_or_create_reader
        
        # Quick test to ensure EasyOCR is working
        try:
            reader = get_or_create_reader(['en'])
            ocr_status = "ready"
        except Exception as e:
            logger.warning(f"OCR initialization check failed: {e}")
            ocr_status = "initializing"
        
        return jsonify({
            "status": "healthy",
            "service": "OCR Service",
            "version": "1.0.0",
            "ocr_status": ocr_status
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "service": "OCR Service",
            "version": "1.0.0",
            "error": str(e)
        }), 503

@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""
    return jsonify({
        "message": "OCR Service API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ocr": "/ocr (POST)"
        }
    }), 200

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    start_time = time.time()
    tmp_path = None
    
    try:
        logger.info("OCR request received")
        
        # Check if file is present
        if "file" not in request.files:
            logger.warning("No file in request")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({"error": "No file selected"}), 400
            
        filename = secure_filename(file.filename)
        if not filename:
            logger.warning("Invalid filename")
            return jsonify({"error": "Invalid filename"}), 400
            
        file_extension = os.path.splitext(filename)[1].lower()
        logger.info(f"Processing file: {filename} (extension: {file_extension})")

        # Validate file type
        if not allowed_file(filename):
            logger.warning(f"Unsupported file type: {file_extension}")
            return jsonify({"error": f"Unsupported file type: {file_extension}. Only PNG, JPG, JPEG, PDF allowed."}), 400

        # Validate file size (limit to 10MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        logger.info(f"File size: {file_length / (1024*1024):.2f} MB")
        
        if file_length > 10 * 1024 * 1024:
            logger.warning(f"File too large: {file_length / (1024*1024):.2f} MB")
            return jsonify({"error": "File too large (max 10MB)"}), 400

        # Parse languages
        languages = request.form.get("lang", "en")
        if isinstance(languages, str):
            languages = [lang.strip() for lang in languages.split(",") if lang.strip()]
        if not languages:
            languages = ["en"]
            
        logger.info(f"Using languages: {languages}")

        # Save file to temporary location
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
            logger.info(f"File saved to: {tmp_path}")

        # Process document
        try:
            logger.info("Starting OCR processing...")
            processing_start = time.time()
            result = process_document(tmp_path, languages)
            processing_time = time.time() - processing_start
            logger.info(f"OCR processing completed in {processing_time:.2f} seconds")
            
            # Add processing metadata
            result["processing_info"] = {
                "processing_time_seconds": round(processing_time, 2),
                "languages_used": languages,
                "file_size_mb": round(file_length / (1024*1024), 2)
            }
            
            total_time = time.time() - start_time
            logger.info(f"Total request time: {total_time:.2f} seconds")
            
            return jsonify(result), 200
            
        except MemoryError as e:
            logger.error(f"Memory error during OCR processing: {e}")
            return jsonify({
                "error": "Processing failed due to memory constraints", 
                "details": "The image is too large or complex to process. Please try a smaller image."
            }), 500
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}", exc_info=True)
            return jsonify({
                "error": "OCR processing failed", 
                "details": str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Request handling failed: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Request processing failed", 
            "details": str(e)
        }), 500
        
    finally:
        # Cleanup
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
                logger.debug(f"Cleaned up temp file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {e}")
        
        # Force garbage collection to free memory
        gc.collect()

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        "error": "File too large", 
        "details": "Maximum file size is 10MB"
    }), 413

@app.errorhandler(500)
def internal_server_error(e):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {e}")
    return jsonify({
        "error": "Internal server error", 
        "details": "Please try again or contact support"
    }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting OCR service on port {port}")
    
    try:
        app.run(debug=False, host="0.0.0.0", port=port, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise