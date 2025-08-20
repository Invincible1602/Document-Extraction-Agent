# File: agentic-document-extraction/app/agent_loop.py
from document_processor import process_document
from extraction import classify_document, extract_fields, validate_extraction
from confidence import ConfidenceCalculator
from schemas import ExtractionResult, FieldSchema, QAReport
from typing import List

def agentic_extraction(file_path: str, fields: List[str] = None, auto_detect: bool = True) -> ExtractionResult:
    processed_doc = process_document(file_path)
    doc_type = "invoice"
    if auto_detect:
        doc_type = classify_document(processed_doc.text)
    extracted_data = extract_fields(processed_doc.text, doc_type, fields)
    validation_report = validate_extraction(extracted_data, processed_doc.text)
    field_schemas = []
    for name, value in extracted_data.items():
        confidence = ConfidenceCalculator.field_confidence(name, value, processed_doc)
        field_schemas.append(FieldSchema(
            name=name,
            value=value,
            confidence=confidence
        ))
    overall_confidence = ConfidenceCalculator.overall_confidence(field_schemas, validation_report)
    return ExtractionResult(
        doc_type=doc_type,
        fields=field_schemas,
        overall_confidence=overall_confidence,
        qa=validation_report
    )
