import streamlit as st
import requests
import json
from typing import Optional, Dict, Any
from datetime import datetime

st.set_page_config(
    page_title="Smart Meeting Upload to N8N",
    page_icon="🧠",
    layout="centered"
)

def validate_file_size(file) -> bool:
    """Validate that file size is less than 25MB"""
    if file is None:
        return False
    
    file_size_mb = file.size / (1024 * 1024)
    return file_size_mb < 25

def extract_text_preview(content: str, max_length: int = 500) -> str:
    """Extract a preview of text content for meeting type prediction"""
    # Clean and truncate for preview
    cleaned = ' '.join(content.split())
    return cleaned[:max_length] + "..." if len(cleaned) > max_length else cleaned

def predict_meeting_type_preview(content: str) -> Dict[str, Any]:
    """Provide a preview of meeting type classification (client-side estimation)"""
    content_lower = content.lower()
    
    # Simple scoring for preview (mirrors the n8n logic)
    scores = {
        'standup': 0,
        'strategy': 0, 
        'client': 0,
        'general': 0
    }
    
    # Standup indicators
    standup_keywords = ['standup', 'daily', 'scrum', 'yesterday', 'today', 'blocker', 'blocked']
    scores['standup'] = sum(2 if keyword in content_lower else 0 for keyword in standup_keywords)
    
    # Strategy indicators  
    strategy_keywords = ['strategy', 'roadmap', 'planning', 'goal', 'objective', 'quarterly']
    scores['strategy'] = sum(2 if keyword in content_lower else 0 for keyword in strategy_keywords)
    
    # Client indicators
    client_keywords = ['client', 'customer', 'proposal', 'contract', 'delivery', 'external']
    scores['client'] = sum(2 if keyword in content_lower else 0 for keyword in client_keywords)
    
    # Determine predicted type
    max_score = max(scores.values())
    predicted_type = 'general' if max_score < 2 else max(scores, key=scores.get)
    confidence = min(max_score / 10, 1.0)
    
    return {
        'predicted_type': predicted_type,
        'confidence': confidence,
        'scores': scores
    }

def format_payload_for_n8n(content: str, file_name: str, upload_type: str, 
                          meeting_title: str = "", attendees: str = "") -> Dict[str, Any]:
    """Format payload to match n8n workflow expectations"""
    timestamp = datetime.now().isoformat()
    
    # Create standardised payload structure
    payload = {
        'transcript': content if upload_type == 'text' else '',
        'text': content if upload_type == 'text' else '',  # Fallback field
        'meetingTitle': meeting_title or f"Uploaded: {file_name}",
        'attendees': attendees or 'Manual Upload',
        'uploadType': upload_type,
        'fileName': file_name,
        'timestamp': timestamp,
        'source': 'streamlit_upload',
        # These fields ensure compatibility with the workflow
        'meetingUrl': '',
        'startTime': timestamp,
        '_structureVersion': '2.0'
    }
    
    return payload

def send_to_n8n(payload: Dict[str, Any], n8n_url: str) -> Dict[str, Any]:
    """Send formatted payload to N8N webhook"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'StreamlitUploader/2.0'
        }
        
        response = requests.post(
            n8n_url, 
            json=payload, 
            headers=headers,
            timeout=120  # Increased timeout for AI processing
        )
        
        response.raise_for_status()
        
        # Try to parse JSON response
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "Upload processed successfully",
            "response": response_data
        }
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out - N8N processing may take longer"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error - check N8N URL"}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def main():
    st.title("🧠 Smart Meeting Upload to N8N")
    st.markdown("Upload meeting content with intelligent type detection and processing")
    
    # Configuration section
    with st.expander("⚙️ Configuration", expanded=True):
        n8n_url = st.text_input(
            "N8N Webhook URL",
            placeholder="https://your-n8n-instance.com/webhook/your-webhook-id",
            help="Your N8N webhook endpoint URL"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            meeting_title = st.text_input(
                "Meeting Title (Optional)",
                placeholder="e.g., Daily Standup, Strategy Review"
            )
        with col2:
            attendees = st.text_input(
                "Attendees (Optional)", 
                placeholder="e.g., Alice, Bob, Charlie"
            )
    
    if not n8n_url:
        st.warning("⚠️ Please enter your N8N webhook URL to continue")
        return
    
    # Upload method selection
    st.subheader("📤 Upload Method")
    upload_method = st.radio(
        "Choose upload method:",
        ["Text Input", "File Upload"],
        horizontal=True
    )
    
    content = ""
    file_name = ""
    
    if upload_method == "Text Input":
        st.subheader("✍️ Direct Text Input")
        content = st.text_area(
            "Meeting Content",
            placeholder="Paste your meeting transcript, notes, or content here...",
            height=200,
            help="Enter the meeting content directly - can be transcripts, notes, or any meeting-related text"
        )
        file_name = "direct_input.txt"
        
    else:  # File Upload
        st.subheader("📁 File Upload")
        file_type = st.selectbox(
            "File Type",
            ["Text File (.txt)", "Audio File (.mp3)"],
            help="Select the type of file you want to upload"
        )
        
        if file_type == "Text File (.txt)":
            uploaded_file = st.file_uploader(
                "Choose a text file",
                type=["txt"],
                help="Upload a .txt file containing meeting content"
            )
            
            if uploaded_file:
                if validate_file_size(uploaded_file):
                    try:
                        content = uploaded_file.read().decode('utf-8')
                        file_name = uploaded_file.name
                        st.success(f"✅ File loaded: {file_name} ({uploaded_file.size / 1024:.1f} KB)")
                    except UnicodeDecodeError:
                        st.error("❌ Cannot read file - please ensure it's a valid text file")
                        return
                else:
                    st.error("❌ File size must be less than 25MB")
                    return
        
        else:  # Audio file
            uploaded_file = st.file_uploader(
                "Choose an audio file",
                type=["mp3"],
                help="Upload a .mp3 audio file for transcription"
            )
            
            if uploaded_file:
                if validate_file_size(uploaded_file):
                    # For audio files, we'll send the binary data
                    content = "AUDIO_FILE_BINARY_DATA"  # Placeholder
                    file_name = uploaded_file.name
                    st.success(f"✅ Audio file ready: {file_name} ({uploaded_file.size / (1024*1024):.1f} MB)")
                    st.info("📝 Audio will be transcribed by N8N workflow")
                else:
                    st.error("❌ File size must be less than 25MB")
                    return
    
    # Content preview and analysis
    if content and content != "AUDIO_FILE_BINARY_DATA":
        st.subheader("🔍 Content Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Content Length", f"{len(content):,} characters")
            st.metric("Word Count", f"{len(content.split()):,} words")
        
        with col2:
            # Show meeting type prediction
            prediction = predict_meeting_type_preview(content)
            st.metric(
                "Predicted Type", 
                prediction['predicted_type'].title(),
                f"{prediction['confidence']:.0%} confidence"
            )
        
        # Content preview
        with st.expander("📄 Content Preview"):
            preview = extract_text_preview(content, 800)
            st.text_area("Preview", preview, height=150, disabled=True)
    
    # Upload section
    if content:
        st.subheader("🚀 Upload to N8N")
        
        if st.button("Process Meeting Content", type="primary", use_container_width=True):
            # Prepare payload
            if upload_method == "File Upload" and content == "AUDIO_FILE_BINARY_DATA":
                # Handle audio file upload differently
                with st.spinner("Uploading audio file for transcription..."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    try:
                        response = requests.post(n8n_url, files=files, timeout=180)
                        response.raise_for_status()
                        result = {
                            "success": True,
                            "status_code": response.status_code,
                            "message": "Audio file uploaded for processing",
                            "response": response.text
                        }
                    except Exception as e:
                        result = {"success": False, "error": str(e)}
            else:
                # Handle text content
                payload = format_payload_for_n8n(
                    content, file_name, "text", meeting_title, attendees
                )
                
                with st.spinner("Processing meeting content..."):
                    result = send_to_n8n(payload, n8n_url)
            
            # Display results
            if result["success"]:
                st.success(f"✅ {result['message']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 Status: {result['status_code']}")
                with col2:
                    st.info(f"⏰ Processed at: {datetime.now().strftime('%H:%M:%S')}")
                
                if result.get("response"):
                    with st.expander("🔍 Server Response"):
                        if isinstance(result["response"], dict):
                            st.json(result["response"])
                        else:
                            st.code(result["response"])
                
                st.balloons()
                
            else:
                st.error(f"❌ Upload failed: {result['error']}")
                
                # Troubleshooting tips
                with st.expander("🔧 Troubleshooting"):
                    st.markdown("""
                    **Common issues:**
                    - Check your N8N webhook URL is correct
                    - Ensure your N8N workflow is active
                    - Verify network connectivity
                    - Check N8N logs for processing errors
                    """)

if __name__ == "__main__":
    main()