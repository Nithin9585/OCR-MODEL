# OCR Backend with Layout Extraction

## 1️⃣ Installation
```bash
pip install -r requirements.txt
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
