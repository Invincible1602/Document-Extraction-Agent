from pydantic import BaseModel, Field
from typing import List, Dict, Any


class FieldSchema(BaseModel):
    name: str
    value: str
    confidence: float = Field(default=0.0, ge=0, le=1)
    source: Dict[str, Any] = Field(
        default_factory=lambda: {"page": 1, "bbox": [0, 0, 0, 0]},
        description="Source location of the field"
    )

    model_config = {"arbitrary_types_allowed": True}


class QAReport(BaseModel):
    passed_rules: List[str] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    notes: str = ""

    model_config = {"arbitrary_types_allowed": True}


class ExtractionResult(BaseModel):
    doc_type: str
    fields: List[FieldSchema]
    overall_confidence: float = Field(default=0.0, ge=0, le=1)
    qa: QAReport = Field(default_factory=QAReport)

    model_config = {"arbitrary_types_allowed": True}


class ProcessedDocument(BaseModel):
    text: str
    pages: List[Dict] = Field(default_factory=list)
    images: List[object] = Field(default_factory=list)
    layout: List[Dict] = Field(default_factory=list)
    ocr_confidences: List[float] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}

    def get_word_confidence(self, bbox: List[float]) -> float:
        if not self.ocr_confidences:
            return 0.8
        return sum(self.ocr_confidences) / len(self.ocr_confidences)
