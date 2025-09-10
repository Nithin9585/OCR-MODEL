# OCR Service - Railway Deployment Ready

## Overview
This directory contains a standalone OCR service that can be deployed on Railway as a microservice.

## Features
- Image OCR processing (PNG, JPG, JPEG, PDF)
- Multi-language support
- Health check endpoint
- Production-ready with Gunicorn

## Railway Deployment Steps

### 1. Create New Railway Project
1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select this repository
5. Choose the `OCR-MODEL` directory as the root

### 2. Deploy Configuration
Railway will automatically:
- Detect the `railway.json` configuration
- Install dependencies from `requirements-railway.txt`
- Start the service with Gunicorn
- Assign a public URL

## 1️⃣ Local Installation
```bash
pip install -r requirements-railway.txt
```

---

## 2️⃣ Start the Server
```bash
python app.py
```
Server will run on `http://localhost:5000`.

---

## 3️⃣ Testing in Postman

### OCR from PDF
- Method: `POST`
- URL: `http://localhost:5000/ocr`
- Body → form-data:
  - **Key:** `file` → Type: *File* → Select your PDF
  - **Key:** `lang` → Type: *Text* → Example: `English,Hindi` or `all`

### OCR from Image
- Same request, just upload a `.png` / `.jpg` / `.pdf`

---

### Example Response
```json
{
  "pages": [
    {
      "page_number": 1,
      "blocks": [
        {
          "text": "Sample Title",
          "position": { "x": 50, "y": 30, "width": 200, "height": 40 },
          "type": "Title"
        },
        {
          "text": "This is a paragraph.",
          "position": { "x": 50, "y": 80, "width": 500, "height": 60 },
          "type": "Paragraph"
        }
      ]
    }
  ]
}
```
