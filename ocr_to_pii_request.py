import json
import uuid

def ocr_to_pii_request(ocr_json, document_id="test-doc", file_type="image"):
    pages = []
    for page in ocr_json.get("pages", []):
        spans = []
        for block in page.get("blocks", []):
            # Convert bounding box to BBox format
            bbox = block["position"]
            x1, y1 = bbox["top_left"]
            x2, y2 = bbox["bottom_right"]
            span = {
                "span_id": str(uuid.uuid4()),
                "text": block["text"],
                "bbox": {
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                },
                "page_no": page.get("page_number", 1),
                "language": "en",
                "ocr_confidence": block.get("confidence", 1.0)
            }
            spans.append(span)
        pages.append({
            "page_no": page.get("page_number", 1),
            "page_size": {},
            "spans": spans
        })
    request = {
        "document_id": document_id,
        "file_type": file_type,
        "pages": pages,
        "options": {
            "entities_to_detect": [
                "AADHAAR", "PAN", "PHONE", "EMAIL", "NAME", "ADDRESS", "AGE", "SEX", "GENDER", "DATE",
                "MEDICAL_RECORD_NUMBER", "PATIENT_ID", "INSURANCE_NUMBER", "ACCOUNT_NUMBER", "MEDICAL_CONDITION",
                "MEDICATION", "TREATMENT_INFO"
            ],
            "use_llm_validation": False,
            "languages": ["en"]
        }
    }
    return request

# Example usage:
# ocr_json = ... # your OCR output
# pii_request = ocr_to_pii_request(ocr_json)
# print(json.dumps(pii_request, indent=2))
