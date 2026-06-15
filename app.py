import tempfile
import os
import streamlit as st
import sys
import json

# Add the scanner folder to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'scanner'))
from scanner import scan_file

# Page config for a modern, dark-themed enterprise look
st.set_page_config(page_title="Enterprise Malware Scanner", page_icon="🛡️", layout="centered")

st.title('🛡️ Enterprise AI Malware Scanner')
st.markdown('### Powered by the EMBER Machine Learning Engine')
st.write('Upload an executable or archive file. Our state-of-the-art LightGBM AI model analyzes 2,351 microscopic features to instantly determine if the file contains malware, ransomware, or malicious payloads.')

# Hide default Streamlit styling to make it look like a standalone app
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.markdown("---")

# Create sidebar for Desktop Agent download
st.sidebar.title("💻 Desktop Agent")
st.sidebar.write("Protect your local endpoint in real-time with our background agent.")

agent_zip_path = os.path.join(os.path.dirname(__file__), "dist", "MalwareDefender_Agent.zip")

if os.path.exists(agent_zip_path):
    with open(agent_zip_path, "rb") as f:
        st.sidebar.download_button(
            label="📥 Download Desktop Agent (ZIP)",
            data=f,
            file_name="MalwareDefender_Agent.zip",
            mime="application/zip",
            help="Contains the standalone executable and the bundled ML models."
        )
else:
    st.sidebar.warning("Desktop agent build not found. Run `pyinstaller malware_defender.spec` to generate it.")

# Expand supported types to match our Phase 7 modular dispatcher!
supported_types = ['exe', 'dll', 'sys', 'zip']
uploaded_file = st.file_uploader(label='Upload Suspicious File', type=supported_types)

# Optional Explainability
show_explanation = st.checkbox("Show AI Decision Explanation (Takes slightly longer)")

if uploaded_file is not None:
    st.markdown("### 🔍 Analysis Report")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Filename:** {uploaded_file.name}")
    with col2:
        st.write(f"**Size:** {uploaded_file.size / 1024:.2f} KB")
        
    st.markdown("---")
    
    with st.spinner("🧠 Scanning 2,351 AI Features..."):
        # 1. Save the uploaded file temporarily to disk
        file_ext = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            # 2. Ask our massive EMBER backend to scan it
            result = scan_file(temp_file_path, explain=show_explanation)
            
            # 3. Display the results with premium UI
            if "error" in result:
                st.error(f"### ❌ Detection failed: {result['error']}")
            else:
                confidence_percent = result['score'] * 100
                
                if result["label"] == "malicious":
                    st.error(f"## 🚨 MALWARE DETECTED")
                    st.error(f"**Confidence Score:** {confidence_percent:.2f}%")
                    st.progress(result['score'])
                else:
                    st.success(f"## ✅ FILE IS SAFE")
                    st.success(f"**Confidence Score:** {confidence_percent:.2f}%")
                    st.progress(result['score'])
                
                # Show SHAP AI Explanation if requested
                if show_explanation and "explanation" in result:
                    st.markdown("### 🤖 AI Reasoning")
                    st.info("The AI flagged these specific features as the most influential in its decision:")
                    
                    # Create a clean table for the explanation
                    explain_data = result["explanation"]
                    st.table([{"Security Category": item["feature"], "Impact Score": f"{item['impact']:.4f}"} for item in explain_data])
                    
                if "explanation_error" in result:
                    st.warning(f"Could not generate AI reasoning: {result['explanation_error']}")

        finally:
            # 4. Clean up the temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)