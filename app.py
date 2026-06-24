import streamlit as st
from extractor import extract_text
from parser import parse_resume

st.set_page_config(page_title="AI Resume Auto-Filler", layout="wide")

st.title("AI Resume Auto-Filler")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.markdown("Supported formats: PDF, DOCX, PNG, JPG, JPEG")

ocr_reader = None

# Step 1: Upload Resume
st.header("1. Upload Resume")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Prepare session state
    if "extracted_data" not in st.session_state or st.session_state.get('last_uploaded_file') != uploaded_file.name:
        st.session_state.extracted_data = None
        st.session_state.raw_text = None
        st.session_state.last_uploaded_file = uploaded_file.name

    file_bytes = uploaded_file.read()
    file_name = uploaded_file.name
    
    # Step 2: Extract Resume Text
    if st.session_state.raw_text is None:
        with st.spinner("Extracting text..."):
            try:
                raw_text = extract_text(file_bytes, file_name)
                st.session_state.raw_text = raw_text
            except Exception as e:
                st.error(f"Error during text extraction: {e}")
                st.stop()
                

    # Step 3: Resume Information Extraction
    if st.session_state.extracted_data is None:
        with st.spinner("Analyzing resume content..."):
            try:
                extracted_data = parse_resume(st.session_state.raw_text)
                st.session_state.extracted_data = extracted_data
            except Exception as e:
                st.error(f"Error during parsing: {e}")
                st.stop()

    data = st.session_state.extracted_data

    # Step 2: Auto-Filled Application Form
    st.header("2. Application Form")
    
    with st.form("application_form"):
        st.subheader("Personal Details")
        name = st.text_input("Full Name", value=data.get('name', ''))
        email = st.text_input("Email", value=data.get('email', ''))
        phone = st.text_input("Phone Number", value=data.get('phone', ''))
        
        st.subheader("Professional Details")
        skills = st.text_area("Skills (Comma-separated)", value=", ".join(data.get('skills', [])))
        experience = st.text_input("Years of Experience", value=data.get('experience', ''))
        current_company = st.text_input("Current Company", value=data.get('current_company', ''))
        
        st.subheader("Education")
        degree = st.text_input("Highest Degree", value=data.get('degree', ''))
        university = st.text_input("College/University", value=data.get('university', ''))
        
        st.subheader("Optional Links")
        linkedin = st.text_input("LinkedIn URL", value=data.get('linkedin', ''))
        github = st.text_input("GitHub URL", value=data.get('github', ''))
        
        # Step 5 & 6: Review & Submit
        submitted = st.form_submit_button("Submit Application")
        
        if submitted:
            final_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "skills": [s.strip() for s in skills.split(",") if s.strip()],
                "experience": experience,
                "current_company": current_company,
                "degree": degree,
                "university": university,
                "linkedin": linkedin,
                "github": github
            }
            
            st.success("Application submitted successfully.")
            st.json(final_data)
