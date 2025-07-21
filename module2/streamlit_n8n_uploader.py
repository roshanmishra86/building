import streamlit as st
import requests
import os
from typing import Optional

st.set_page_config(
    page_title="File Upload to N8N",
    page_icon="📤",
    layout="centered"
)

def validate_file_size(file) -> bool:
    """Validate that file size is less than 25MB"""
    if file is None:
        return False
    
    file_size_mb = file.size / (1024 * 1024)
    return file_size_mb < 25

def send_to_n8n(file, n8n_url: str, file_type: str) -> dict:
    """Send file to N8N webhook URL"""
    try:
        if file_type == "text":
            # For text files, send as multipart form data
            files = {"file": (file.name, file.getvalue(), file.type)}
            response = requests.post(n8n_url, files=files, timeout=60)
        else:
            # For audio files, send as binary data
            files = {"file": (file.name, file.getvalue(), file.type)}
            response = requests.post(n8n_url, files=files, timeout=60)
        
        response.raise_for_status()
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "File uploaded successfully",
            "response": response.text if response.text else "No response content"
        }
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error - check N8N URL"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def main():
    st.title("📤 File Upload to N8N")
    st.markdown("Upload text data or audio files (< 25MB) to your N8N workflow")
    
    # N8N URL configuration
    n8n_url = st.text_input(
        "N8N Webhook URL",
        placeholder="https://your-n8n-instance.com/webhook/your-webhook-id",
        help="Enter your N8N webhook URL"
    )
    
    if not n8n_url:
        st.warning("Please enter your N8N webhook URL to continue")
        return
    
    # File upload options
    upload_type = st.radio(
        "Choose upload type:",
        ["Text File", "Audio File"],
        horizontal=True
    )
    
    if upload_type == "Text File":
        uploaded_file = st.file_uploader(
            "Choose a text file",
            type=["txt"],
            help="Only .txt files are supported"
        )
        file_type = "text"
    else:
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=["mp3"],
            help="Only .mp3 files are supported"
        )
        file_type = "audio"
    
    if uploaded_file is not None:
        # File information
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type or "Unknown")
        
        # File size validation
        if not validate_file_size(uploaded_file):
            st.error("❌ File size must be less than 25MB")
            return
        else:
            st.success("✅ File size is valid")
        
        # Preview for text files
        if file_type == "text" and file_size_mb < 1:  # Only preview small text files
            with st.expander("File Preview"):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    st.text_area("Content Preview", content[:1000] + "..." if len(content) > 1000 else content, height=200)
                    uploaded_file.seek(0)  # Reset file pointer
                except UnicodeDecodeError:
                    st.warning("Cannot preview file - contains non-text data")
        
        # Upload button
        if st.button("🚀 Upload to N8N", type="primary"):
            with st.spinner("Uploading file..."):
                result = send_to_n8n(uploaded_file, n8n_url, file_type)
            
            if result["success"]:
                st.success(f"✅ {result['message']}")
                st.info(f"Status Code: {result['status_code']}")
                if result["response"]:
                    with st.expander("Server Response"):
                        st.code(result["response"])
            else:
                st.error(f"❌ Upload failed: {result['error']}")

if __name__ == "__main__":
    main()