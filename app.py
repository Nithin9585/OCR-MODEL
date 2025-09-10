import os
import tempfile
import warnings

from flask import Flask, request, jsonify
from ocr_processor import process_document
from werkzeug.utils import secure_filename
import logging

# Suppress all warnings and logging
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
os.environ['PYTHONWARNINGS'] = 'ignore'

app = Flask(__name__)
# Disable Flask logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Configure for production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Minimal startup - no preloading to save memory


def allowed_file(filename):
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
    return os.path.splitext(filename)[1].lower() in allowed_extensions

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        "status": "healthy",
        "service": "OCR Service",
        "version": "1.0.0"
    }), 200

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
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]


    # Validate file type
    if not allowed_file(filename):
        return jsonify({"error": "Unsupported file type. Only PNG, JPG, JPEG, PDF allowed."}), 400

    # Validate file size (limit to 10MB)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    if file_length > 10 * 1024 * 1024:
        return jsonify({"error": "File too large (max 10MB)"}), 400

    languages = request.form.get("lang", None)
    if languages:
        languages = [lang.strip() for lang in languages.split(",")]
    else:
        languages = ["en"]

    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        try:
            result = process_document(tmp_path, languages)
        except Exception as e:
            # Silent error handling - no logging
            return jsonify({"error": "OCR processing failed"}), 500
        return jsonify(result)
    finally:
        os.remove(tmp_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)