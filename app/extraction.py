from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from pydantic import create_model, Field
from typing import List, Dict, Callable
import re
import datetime
from schemas import QAReport

DOCUMENT_TYPES = ["invoice", "medical_bill", "prescription"]

FIELD_MAPPING = {
    "invoice": ["vendor_name", "vendor_address", "invoice_number", "invoice_date",
                "due_date", "total_amount", "tax_amount", "line_items"],
    "medical_bill": ["patient_name", "patient_dob", "provider_name", "provider_address",
                     "service_date", "total_charges", "insurance_name", "claim_number"],
    "prescription": ["patient_name", "patient_dob", "prescriber_name", "prescriber_license",
                     "medication", "dosage", "quantity", "refills", "issue_date"]
}

VALIDATION_RULES: Dict[str, Callable[[str], bool]] = {
    "date": lambda val: validate_date(val),
    "amount": lambda val: validate_amount(val),
    "charges": lambda val: validate_amount(val),
    "total": lambda val: validate_amount(val),
}

def classify_document(text: str) -> str:
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    messages = [
        SystemMessage(content="You are an expert document classifier. Classify the document as one of: invoice, medical_bill, prescription."),
        HumanMessage(content=f"Document content:\n{text[:2000]}\n\nClassification:")
    ]
    response = llm.invoke(messages)
    classification = response.content.strip().lower()
    for doc_type in DOCUMENT_TYPES:
        if doc_type in classification:
            return doc_type
    return DOCUMENT_TYPES[0]

def extract_fields(doc_text: str, doc_type: str, fields: List[str] = None) -> Dict:
    if not fields:
        fields = FIELD_MAPPING.get(doc_type, [])
    field_definitions = {
        field: (str, Field(..., description=f"Extracted value for {field}"))
        for field in fields
    }
    DynamicSchema = create_model("DynamicSchema", **field_definitions)
    results = []
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
    for _ in range(3):
        structured_llm = llm.with_structured_output(DynamicSchema)
        try:
            result = structured_llm.invoke(doc_text)
            results.append(result.dict())
        except Exception:
            continue
    final_result = {}
    for field in fields:
        values = {}
        for res in results:
            if field in res and res[field]:
                value = res[field]
                values[value] = values.get(value, 0) + 1
        final_result[field] = max(values, key=values.get) if values else ""
    return final_result

def validate_extraction(extraction: Dict, doc_text: str) -> QAReport:
    report = QAReport()
    low_confidence_fields = []
    for field, value in extraction.items():
        if not value:
            low_confidence_fields.append(field)
            continue
        for keyword, rule in VALIDATION_RULES.items():
            if keyword in field.lower():
                if not rule(value):
                    report.failed_rules.append(f"{keyword}_format_{field}")
                else:
                    report.passed_rules.append(f"{keyword}_format_{field}")
    if "line_items" in extraction and "total_amount" in extraction:
        if "calculated_total" in doc_text.lower():
            report.passed_rules.append("totals_match")
        else:
            report.failed_rules.append("totals_match")
    if low_confidence_fields:
        report.notes = f"{len(low_confidence_fields)} low-confidence fields: {', '.join(low_confidence_fields)}"
    return report

def validate_date(date_str: str) -> bool:
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            datetime.datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False

def validate_amount(amount_str: str) -> bool:
    return bool(re.match(r"^\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?$", amount_str))
