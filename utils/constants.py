# File: agentic-document-extraction/utils/constants.py

SUPPORTED_FILE_TYPES = [".pdf", ".png", ".jpg", ".jpeg"]

DEFAULT_FIELDS = {
    "invoice": [
        "vendor_name",
        "vendor_address",
        "vendor_contact",
        "vendor_email",
        "vendor_phone",
        "vendor_tax_id",
        "vendor_gst_number",

        "customer_name",
        "customer_address",
        "customer_contact",
        "customer_email",
        "customer_phone",
        "customer_tax_id",
        "customer_gst_number",

        "invoice_number",
        "invoice_date",
        "due_date",
        "purchase_order_number",
        "delivery_note_number",
        "terms_and_conditions",

        "subtotal",
        "discount",
        "taxable_amount",
        "tax_rate",
        "tax_amount",
        "shipping_charges",
        "other_charges",
        "total_amount",
        "amount_due",
        "amount_paid",
        "currency",

        "item_description",
        "item_code",
        "item_quantity",
        "item_unit_price",
        "item_total"
    ],

    "medical_bill": [
        "patient_name",
        "patient_id",
        "patient_address",
        "patient_contact",
        "patient_age",
        "patient_gender",
        "patient_insurance_id",

        "provider_name",
        "provider_address",
        "provider_contact",
        "provider_tax_id",
        "provider_license_number",

        "bill_number",
        "service_date",
        "admission_date",
        "discharge_date",
        "bill_date",

        "procedure_code",
        "procedure_description",
        "diagnosis_code",
        "diagnosis_description",
        "medication_name",
        "medication_quantity",
        "medication_cost",

        "room_charges",
        "consultation_fees",
        "surgery_fees",
        "lab_charges",
        "radiology_charges",
        "other_charges",
        "total_charges",

        "insurance_name",
        "insurance_policy_number",
        "insurance_claim_number",
        "amount_covered_by_insurance",
        "amount_due_from_patient",
        "payment_status"
    ],

    "prescription": [
        "patient_name",
        "patient_id",
        "patient_age",
        "patient_gender",
        "patient_address",
        "patient_contact",

        "prescriber_name",
        "prescriber_id",
        "prescriber_license_number",
        "prescriber_address",
        "prescriber_contact",
        "prescriber_specialization",

        "prescription_number",
        "issue_date",
        "valid_until",
        "refill_allowed",
        "refill_count",

        "medication_name",
        "medication_generic_name",
        "medication_strength",
        "dosage",
        "frequency",
        "route_of_administration",
        "duration",
        "quantity",
        "instructions",
        "substitution_allowed",

        "pharmacy_name",
        "pharmacy_address",
        "pharmacy_contact",

        "signature",
        "stamp"
    ]
}


OCR_API_ENDPOINT = "https://api.ocr.space/parse/image"
