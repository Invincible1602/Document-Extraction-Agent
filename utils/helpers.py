# File: agentic-document-extraction/utils/helpers.py
import re
import datetime

def clean_text(text: str) -> str:
    """Clean OCR text output"""
    text = re.sub(r'\s+', ' ', text)  # remove excessive whitespace
    text = re.sub(r'[^\x20-\x7E]', '', text)  # remove non-printable characters
    return text.strip()

def validate_date(date_str: str) -> bool:
    """Validate multiple date formats"""
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y",
        "%d-%m-%Y", "%m-%d-%Y", "%d.%m.%Y",
        "%b %d, %Y", "%d %b %Y", "%B %d, %Y"
    ]
    for fmt in formats:
        try:
            datetime.datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

def normalize_date(date_str: str) -> str:
    """Convert various date formats to ISO (YYYY-MM-DD)"""
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y",
        "%d-%m-%Y", "%m-%d-%Y", "%d.%m.%Y",
        "%b %d, %Y", "%d %b %Y", "%B %d, %Y"
    ]
    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str  # return as-is if not parsed

def format_confidence(confidence: float) -> str:
    """Format confidence as percentage"""
    return f"{confidence * 100:.1f}%"

def extract_currency(text: str) -> str:
    """Extract currency symbols or codes"""
    match = re.search(r'(\$|USD|EUR|£|INR|¥|CAD|AUD)', text, re.IGNORECASE)
    return match.group(1).upper() if match else ""

def extract_amount(text: str) -> str:
    """Extract monetary amount"""
    match = re.search(r'([0-9]+(?:[\.,][0-9]{2})?)', text)
    return match.group(1) if match else ""

def extract_email(text: str) -> str:
    """Extract email address"""
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    return match.group(0) if match else ""

def extract_phone(text: str) -> str:
    """Extract phone number"""
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
    return match.group(0) if match else ""

def extract_invoice_number(text: str) -> str:
    """Extract invoice/bill number"""
    match = re.search(r'(Invoice|Bill|Receipt|Claim)[\s#:]*([A-Za-z0-9-]+)', text, re.IGNORECASE)
    return match.group(2) if match else ""

def extract_id_fields(text: str) -> dict:
    """Extract generic IDs like invoice number, prescription ID, claim number"""
    fields = {}
    fields["invoice_number"] = extract_invoice_number(text)
    fields["email"] = extract_email(text)
    fields["phone"] = extract_phone(text)
    return {k: v for k, v in fields.items() if v}
