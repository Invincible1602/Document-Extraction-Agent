# Document-Extraction-Agent

# 📄 Document Extraction Agent

An AI-powered Python project to **extract structured data from documents** such as invoices, medical bills, and prescriptions. The app provides **confidence scoring and validation** for each extracted field. It features a **Streamlit UI** and supports **Google Gemini** API for deployment and Hugging Face models for local testing.

---

## Features

- Upload documents in PDF, PNG, JPG, or JPEG format
- Automatic document type detection (Invoice, Medical Bill, Prescription)
- AI-powered field extraction using:
  - **Google Gemini** (for deployment)
  - **Hugging Face GPT-OSS-20B** (for local testing)
- Confidence scoring and validation rules for extracted data
- Download results as JSON
- Clean and interactive Streamlit UI

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Invincible1602/Document-Extraction-Agent.git
cd Document-Extraction-Agent/app
```

## Project Structure

```bash
app/
├── main.py            # Streamlit frontend
├── extraction.py      # LLM-based extraction logic
├── agent_loop.py      # Orchestrates document processing
├── document_processor.py  # Handles PDF/image parsing
├── schemas.py         # Pydantic models for structured output
├── confidence.py      # Confidence scoring logic
└── requirements.txt
utils/
├── helpers.py # Text cleaning, date/amount validation, and other helpers
└── constants.py # Constants like supported file types, default fields
```