import tempfile
import os
import streamlit as st
import sys

# Add the scanner folder to the path so we can import our new module
sys.path.append(os.path.join(os.path.dirname(__file__), 'scanner'))
from scanner import scan_file

st.title('Ransomware Detect')
st.markdown('### What we do?')
st.write('We will scan the .exe files and determine whether the file has malware or not')

# Hide default Streamlit styling
hide_streamlit_style = """
            <style>
           #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

exe_upload = st.file_uploader(label='Upload .exe File', type='exe')

if exe_upload is not None:
    st.write(f"File uploaded: {exe_upload.name}")
    st.write(f"File size: {exe_upload.size} bytes")
    
    # 1. Save the uploaded file temporarily to disk
    with tempfile.NamedTemporaryFile(delete=False, suffix='.exe') as temp_file:
        temp_file.write(exe_upload.read())
        temp_file_path = temp_file.name

    try:
        # 2. Ask our new backend to scan it!
        result = scan_file(temp_file_path)
        
        # 3. Display the results
        if "error" in result:
            st.error(f"### Detection failed: {result['error']}")
        else:
            if result["label"] == "malicious":
                st.error(f"### 🚨 Ransomware detection result: {result['label'].upper()} (Confidence: {result['score']*100:.2f}%)")
            else:
                st.success(f"### ✅ Ransomware detection result: {result['label'].upper()} (Confidence: {result['score']*100:.2f}%)")
    finally:
        # 4. Clean up the temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)