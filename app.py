import os
import tempfile

from flask import Flask, request, jsonify
from ocr_processor import process_document
from werkzeug.utils import secure_filename
import logging


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def allowed_file(filename):
    allowed_extensions = {'.png', '.jpg', '.jpeg'}
    return os.path.splitext(filename)[1].lower() in allowed_extensions

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]


    # Validate file type
    if not allowed_file(filename):
        return jsonify({"error": "Unsupported file type. Only PNG, JPG, JPEG allowed."}), 400

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
            logging.error(f"OCR processing failed: {e}")
            return jsonify({"error": "OCR processing failed", "details": str(e)}), 500
        return jsonify(result)
    finally:
        os.remove(tmp_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)