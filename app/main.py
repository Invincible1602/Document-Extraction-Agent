import streamlit as st
import tempfile
import json
import os
from dotenv import load_dotenv
from agent_loop import agentic_extraction

load_dotenv()

st.set_page_config(page_title="DocuExtract AI", layout="wide")

st.title("📄 Agentic Document Extraction")
st.caption("Extract structured data from documents with AI-powered validation")

with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader(
        "Upload document", 
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=False
    )
    fields_input = st.text_input(
        "Fields to extract (comma separated, leave blank for auto-detection)"
    )
    auto_detect = st.checkbox("Auto-detect document type", True)
    st.divider()
    st.markdown("**Advanced Options**")
    show_debug = st.checkbox("Show debug information", False)
    run_button = st.button("Extract Data", type="primary")

if uploaded_file and run_button:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        file_path = tmp_file.name
    
    fields = [f.strip() for f in fields_input.split(",")] if fields_input else None
    
    with st.spinner("Processing document..."):
        try:
            result = agentic_extraction(file_path, fields, auto_detect)
        except Exception as e:
            st.error(f"Error during extraction: {str(e)}")
            st.stop()
    
    st.subheader("Extraction Results")
    st.json(result.model_dump())
    
    st.download_button(
        label="Download JSON",
        data=json.dumps(result.model_dump(), indent=2),
        file_name="extraction_result.json",
        mime="application/json"
    )
    
    st.subheader("Confidence Analysis")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Overall Confidence", f"{result.overall_confidence*100:.1f}%")
    with col2:
        st.progress(result.overall_confidence)
    
    for field in result.fields:
        col1, col2 = st.columns([2, 4])
        with col1:
            st.markdown(f"**{field.name}**")
            st.code(field.value, language="text")
        with col2:
            st.caption(f"Confidence: {field.confidence*100:.1f}%")
            st.progress(field.confidence)
    
    st.subheader("Validation Report")
    if result.qa.passed_rules:
        st.success(f"**Passed rules:** {', '.join(result.qa.passed_rules)}")
    if result.qa.failed_rules:
        st.error(f"**Failed rules:** {', '.join(result.qa.failed_rules)}")
    if result.qa.notes:
        st.warning(result.qa.notes)
    
    if show_debug:
        st.subheader("Debug Information")
        st.json(result.model_dump(mode="json"))

else:
    st.info("Upload a document and click 'Extract Data' to begin")
    with st.expander("Sample Document Formats"):
        st.markdown("""
        - **Invoices**: Should contain vendor info, line items, totals  
        - **Medical Bills**: Patient info, provider, charges, insurance  
        - **Prescriptions**: Patient info, medication, dosage, refills  
        """)

if __name__ == "__main__":
    st.write("App is running")
