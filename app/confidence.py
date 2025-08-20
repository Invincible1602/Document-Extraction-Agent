# File: agentic-document-extraction/app/confidence.py
from schemas import ProcessedDocument, FieldSchema, QAReport
from typing import List, Dict
import datetime
import re

class ConfidenceCalculator:
    @staticmethod
    def field_confidence(field_name: str, field_value: str, doc: ProcessedDocument) -> float:
        presence_conf = 1.0 if field_value else 0.2
        length_conf = min(1.0, len(field_value) / 20)
        ocr_conf = doc.get_word_confidence([0, 0, 0, 0])
        type_boost = 1.0
        if "date" in field_name and validate_date(field_value):
            type_boost = 1.2
        elif ("amount" in field_name or "total" in field_name) and validate_amount(field_value):
            type_boost = 1.2
        confidence = (presence_conf * 0.4) + (length_conf * 0.3) + (ocr_conf * 0.3)
        return min(1.0, confidence * type_boost)

    @staticmethod
    def overall_confidence(fields: List[FieldSchema], qa: QAReport) -> float:
        field_weights = {
            "total_amount": 1.5,
            "invoice_number": 1.3,
            "patient_name": 1.4,
            "medication": 1.4,
            "date": 1.2
        }
        total_weight = 0
        weighted_sum = 0
        for field in fields:
            weight = field_weights.get(field.name, 1.0)
            weighted_sum += field.confidence * weight
            total_weight += weight
        base_confidence = weighted_sum / total_weight if total_weight > 0 else 0
        validation_factor = 1.0
        if qa.failed_rules:
            validation_factor = max(0.7, 1.0 - (len(qa.failed_rules) * 0.1))
        return min(1.0, base_confidence * validation_factor)

def validate_date(date_str: str) -> bool:
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except:
        return False

def validate_amount(amount_str: str) -> bool:
    return bool(re.match(r"^\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?$", amount_str))
