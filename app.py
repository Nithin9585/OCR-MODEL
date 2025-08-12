import os
import tempfile
from flask import Flask, request, jsonify
from ocr_processor import process_document
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr_endpoint():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    languages = request.form.get("lang", None)

    if languages:
        languages = [lang.strip() for lang in languages.split(",")]
    else:
        languages = ["en"]

    # Get a secure filename and its extension
    filename = secure_filename(file.filename)
    file_extension = os.path.splitext(filename)[1]

    # Create a temporary file with the correct extension
    # This is the crucial change!
    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Pass the path to the OCR processor
        result = process_document(tmp_path, languages)
        return jsonify(result)
    finally:
        # Ensure the temporary file is deleted
        os.remove(tmp_path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)