# File: agentic-document-extraction/app/document_processor.py
import pdf2image
import requests
import io
import os
from PIL import Image
from schemas import ProcessedDocument
import time
import logging
import dotenv
from google import genai
from google.genai import types

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

OCR_API_KEY = os.getenv("OCR_API_KEY")
if not OCR_API_KEY:
    raise EnvironmentError("OCR_API_KEY environment variable is not set")

OCR_API_ENDPOINT = "https://api.ocr.space/parse/image"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY environment variable is not set")

gemini_client = genai.Client(api_key=GOOGLE_API_KEY)


def ocr_with_api(image: Image) -> dict:
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format="JPEG", quality=85)
    img_byte_arr = img_byte_arr.getvalue()
    files = {"file": ("image.jpg", img_byte_arr, "image/jpeg")}
    data = {
        "language": "eng",
        "isOverlayRequired": "true",
        "detectOrientation": "true",
        "isTable": "true",
        "OCREngine": "2"
    }
    try:
        response = requests.post(
            OCR_API_ENDPOINT,
            headers={"apikey": OCR_API_KEY},
            files=files,
            data=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        if result.get("IsErroredOnProcessing"):
            err = result.get("ErrorMessage", "Unknown OCR error")
            raise RuntimeError(f"OCR API failed: {err}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"OCR API error: {e}")
        raise RuntimeError("OCR processing failed") from e


def process_with_gemini(text: str) -> str:
    """Send OCR text to Gemini and return structured extraction."""
    try:
        prompt = (
            "Extract structured key-value information from this document text. "
            "Return JSON with clear keys and values only.\n\n"
            f"{text}"
        )
        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash",  # or gemini-2.5-flash if enabled
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024,
            ),
        )
        if response.candidates:
            return response.candidates[0].content.parts[0].text
        return ""
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return ""


def process_document(file_path: str) -> ProcessedDocument:
    if file_path.lower().endswith(".pdf"):
        images = pdf2image.convert_from_path(file_path, dpi=300)
    else:
        images = [Image.open(file_path)]
    processed_pages = []
    all_text = []
    confidences = []
    for page_num, img in enumerate(images):
        if img.mode != "RGB":
            img = img.convert("RGB")
        ocr_data = ocr_with_api(img)
        parsed_results = ocr_data.get("ParsedResults", [])
        if parsed_results:
            page_text = parsed_results[0].get("ParsedText", "")
            overlay = parsed_results[0].get("TextOverlay", {}).get("Lines", [])
        else:
            page_text, overlay = "", []
        all_text.append(page_text)
        words_info = []
        page_confidences = []
        for line in overlay:
            for word in line.get("Words", []):
                text = word.get("WordText", "").strip()
                if text:
                    confidence = 0.9
                    bbox = [
                        word.get("Left", 0),
                        word.get("Top", 0),
                        word.get("Left", 0) + word.get("Width", 0),
                        word.get("Top", 0) + word.get("Height", 0),
                    ]
                    words_info.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })
                    page_confidences.append(confidence)
        confidences.extend(page_confidences)
        processed_pages.append({
            "page": page_num + 1,
            "text": page_text,
            "words": words_info,
            "layout": overlay
        })
        time.sleep(1)

    full_text = "\n\n".join(all_text)
    gemini_output = process_with_gemini(full_text)

    return ProcessedDocument(
        text=full_text,
        pages=processed_pages,
        images=images,
        ocr_confidences=confidences,
        gemini_output=gemini_output
    )
