import tempfile
import os
import streamlit as st
import sys
import json

# Add root to sys.path so we can import engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine.scanner import scan_file

# Page config for a modern, dark-themed enterprise look
st.set_page_config(page_title="Aegis Sentinel", page_icon="🛡️", layout="centered")

st.title('🛡️ Aegis Sentinel')
st.markdown('### Powered by the EMBER Machine Learning Engine')
st.write('Upload an executable or archive file. Our state-of-the-art LightGBM ML model analyzes 2,351 microscopic features to instantly determine if the file contains malware, ransomware, or malicious payloads.')

# Hide default Streamlit styling to make it look like a standalone app
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Desktop Agent Download Section (Moved from sidebar to main UI for better mobile responsiveness)
with st.expander("💻 Download Desktop Agent (Real-Time Protection)", expanded=False):
    st.write("Protect your local Windows endpoint in real-time with our background Watchdog daemon. No Python installation required.")
    
    st.markdown("""
    <div style="background-color: #2b2b2b; padding: 20px; border-radius: 10px; border: 1px solid #444; text-align: center; margin-top: 10px; margin-bottom: 10px;">
        <h3 style="margin-top: 0; color: white;">📥 Aegis Sentinel Standalone Agent</h3>
        <p style="color: #bbb; font-size: 14px;">Download the compiled `.exe` directly from our GitHub Releases CDN.</p>
        <a href="https://github.com/Vavaldas-jaiwanth/Aegis-Sentinel/releases/latest/download/AegisSentinel_Agent.zip" target="_blank" style="display: inline-block; padding: 12px 24px; color: white; background-color: #FF4B4B; text-align: center; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(255, 75, 75, 0.3);">
            Download AegisSentinel_Agent.zip
        </a>
    </div>
    """, unsafe_allow_html=True)

    agent_zip_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist", "AegisSentinel_Agent.zip")
    if os.path.exists(agent_zip_path):
        st.success(f"✅ **Local Build Detected:** `{agent_zip_path}`")
        st.info("To avoid crashing Streamlit with a 260MB MemoryError, please manually navigate to the `dist/` folder to access your local build.")

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
                    
                    formatted_data = []
                    for item in explain_data:
                        impact = item['impact']
                        if impact > 0:
                            interpretation = f"🔴 Suspicious (+{impact:.2f} towards Malware)"
                        else:
                            interpretation = f"🟢 Legitimate ({impact:.2f} towards Safe)"
                            
                        formatted_data.append({
                            "Security Category": item["feature"],
                            "AI Interpretation": interpretation
                        })
                        
                    st.table(formatted_data)
                    
                if "explanation_error" in result:
                    st.warning(f"Could not generate AI reasoning: {result['explanation_error']}")

        finally:
            # 4. Clean up the temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)