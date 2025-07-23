import streamlit as st
import requests
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Smart Meeting Processor",
    page_icon="🧠",
    layout="centered"
)

def validate_file_size(file) -> bool:
    """Validate that file size is less than 25MB"""
    if file is None:
        return False
    file_size_mb = file.size / (1024 * 1024)
    return file_size_mb < 25

def validate_file_type(file) -> bool:
    """Validate file type - only allow mp3, wav, txt"""
    if file is None:
        return False
    
    allowed_extensions = ['.txt', '.mp3', '.wav']
    file_extension = file.name.lower()
    return any(file_extension.endswith(ext) for ext in allowed_extensions)

def predict_meeting_type(content: str) -> Dict[str, Any]:
    """Predict meeting type from content"""
    if not content or len(content.strip()) < 10:
        return {'predicted_type': 'general', 'confidence': 0.1}
    
    content_lower = content.lower()
    
    # Scoring system
    scores = {
        'standup': 0,
        'strategy': 0, 
        'client': 0,
        'general': 0
    }
    
    # Keyword matching with weights
    keywords = {
        'standup': ['standup', 'daily', 'scrum', 'yesterday', 'today', 'blocker', 'blocked', 'sprint'],
        'strategy': ['strategy', 'roadmap', 'planning', 'goal', 'objective', 'quarterly', 'vision', 'initiative'],
        'client': ['client', 'customer', 'proposal', 'contract', 'delivery', 'external', 'requirement', 'feedback']
    }
    
    for meeting_type, words in keywords.items():
        for word in words:
            if word in content_lower:
                scores[meeting_type] += 2
    
    # Determine predicted type
    max_score = max(scores.values())
    predicted_type = 'general' if max_score < 2 else max(scores, key=scores.get)
    confidence = min(max_score / 10, 1.0)
    
    return {
        'predicted_type': predicted_type,
        'confidence': confidence,
        'scores': scores
    }

def send_text_to_n8n(content: str, file_name: str, meeting_title: str, attendees: str, n8n_url: str) -> Dict[str, Any]:
    """Send text content to N8N webhook"""
    payload = {
        'transcript': content,
        'text': content,
        'meetingTitle': meeting_title or f"Uploaded: {file_name}",
        'attendees': attendees or 'Manual Upload',
        'fileName': file_name,
        'timestamp': datetime.now().isoformat(),
        'source': 'streamlit_upload',
        'uploadType': 'text',
        'meetingUrl': '',
        'startTime': datetime.now().isoformat(),
        '_structureVersion': '2.0'
    }
    
    return make_request(n8n_url, json_payload=payload)

def send_audio_to_n8n(file, meeting_title: str, attendees: str, n8n_url: str) -> Dict[str, Any]:
    """Send audio file to N8N webhook"""
    try:
        # Read file content
        file_content = file.getvalue()
        
        # Prepare multipart form data
        files = {
            'file': (file.name, file_content, file.type or 'audio/mpeg')
        }
        
        # Additional form data
        form_data = {
            'meetingTitle': meeting_title or f"Audio: {file.name}",
            'attendees': attendees or 'Manual Upload',
            'fileName': file.name,
            'timestamp': datetime.now().isoformat(),
            'source': 'streamlit_upload',
            'uploadType': 'audio',
            '_structureVersion': '2.0'
        }
        
        return make_request(n8n_url, files=files, form_data=form_data)
        
    except Exception as e:
        return {"success": False, "error": f"Audio file processing error: {str(e)}"}

def make_request(url: str, json_payload=None, files=None, form_data=None) -> Dict[str, Any]:
    """Make HTTP request to N8N webhook"""
    try:
        headers = {'User-Agent': 'StreamlitProcessor/1.0'}
        
        if json_payload:
            headers['Content-Type'] = 'application/json'
            response = requests.post(url, json=json_payload, headers=headers, timeout=180)
        else:
            # For file uploads, don't set Content-Type - let requests handle it
            response = requests.post(url, files=files, data=form_data, headers={'User-Agent': 'StreamlitProcessor/1.0'}, timeout=180)
        
        response.raise_for_status()
        
        # Try to parse JSON response
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "Processing completed successfully",
            "response": response_data
        }
    
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out - N8N processing may take longer than expected"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error - please check your N8N URL"}
    except requests.exceptions.HTTPError as e:
        error_text = ""
        try:
            error_text = e.response.text[:500]
        except:
            pass
        return {"success": False, "error": f"HTTP {e.response.status_code}: {error_text}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def display_results(result: Dict[str, Any]):
    """Display processing results"""
    if result["success"]:
        st.success("✅ Processing completed successfully!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status Code", result['status_code'])
        with col2:
            st.metric("Processed At", datetime.now().strftime('%H:%M:%S'))
        
        if result.get("response"):
            with st.expander("🔍 Processing Results", expanded=True):
                response_data = result["response"]
                
                # Try to display structured data if available
                if isinstance(response_data, dict):
                    # Check for action items
                    if 'actionItems' in response_data:
                        st.subheader("📋 Action Items")
                        for item in response_data['actionItems']:
                            with st.container():
                                st.markdown(f"**{item.get('actionItem', 'N/A')}**")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.text(f"Owner: {item.get('owner', 'N/A')}")
                                with col2:
                                    st.text(f"Due: {item.get('dueDate', 'N/A')}")
                                with col3:
                                    st.text(f"Priority: {item.get('priority', 'N/A')}")
                                st.divider()
                    
                    # Check for summary
                    if 'summaryRecord' in response_data:
                        st.subheader("📊 Executive Summary")
                        summary = response_data['summaryRecord']
                        st.markdown(f"**Meeting Type:** {summary.get('meetingType', 'N/A')}")
                        st.markdown(f"**Key Decisions:** {summary.get('keyDecisions', 'N/A')}")
                        st.markdown(f"**Executive Summary:** {summary.get('executiveSummary', 'N/A')}")
                        st.markdown(f"**Next Steps:** {summary.get('nextSteps', 'N/A')}")
                    
                    # Show full response in expandable section
                    with st.expander("🔧 Full Response Data"):
                        st.json(response_data)
                else:
                    st.code(str(response_data))
        
        st.balloons()
        
    else:
        st.error(f"❌ Processing failed: {result['error']}")
        
        with st.expander("🔧 Troubleshooting Tips"):
            st.markdown("""
            **Common issues and solutions:**
            - **Connection Error**: Verify your N8N webhook URL is correct and accessible
            - **Timeout**: Large files or complex processing may take longer - try smaller files
            - **HTTP 4xx/5xx**: Check N8N workflow is active and properly configured
            - **File Issues**: Ensure file is under 25MB and in supported format (txt, mp3, wav)
            """)

def main():
    st.title("🧠 Smart Meeting Processor")
    st.markdown("Upload meeting content for intelligent analysis and action item extraction")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        n8n_url = st.text_input(
            "N8N Webhook URL *",
            placeholder="https://your-n8n-instance.com/webhook/your-webhook-id",
            help="Your N8N webhook endpoint URL (required)",
            type="password"
        )
        
        st.subheader("Meeting Details (Optional)")
        meeting_title = st.text_input(
            "Meeting Title",
            placeholder="e.g., Daily Standup, Strategy Review"
        )
        attendees = st.text_input(
            "Attendees", 
            placeholder="e.g., Alice, Bob, Charlie"
        )
        
        if not n8n_url:
            st.warning("⚠️ N8N webhook URL is required")
    
    if not n8n_url:
        st.info("👈 Please configure your N8N webhook URL in the sidebar to continue")
        st.stop()
    
    # Main content area
    st.subheader("📤 Upload Method")
    upload_method = st.radio(
        "Choose how you'd like to provide meeting content:",
        ["Direct Text Input", "File Upload"],
        horizontal=True
    )
    
    content = ""
    file_name = "direct_input.txt"
    uploaded_file = None
    
    if upload_method == "Direct Text Input":
        st.subheader("✍️ Text Input")
        content = st.text_area(
            "Meeting Content",
            placeholder="Paste your meeting transcript, notes, or content here...\n\nExample:\n- Yesterday I worked on the API integration\n- Today I'm focusing on the database optimization\n- I'm blocked on the authentication service",
            height=250,
            help="Enter meeting content - can be transcripts, notes, or any meeting-related text"
        )
        
        if content:
            # Show content analysis
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Character Count", f"{len(content):,}")
            with col2:
                prediction = predict_meeting_type(content)
                st.metric("Predicted Type", prediction['predicted_type'].title())
        
    else:  # File Upload
        st.subheader("📁 File Upload")
        st.info("Supported formats: Text files (.txt), Audio files (.mp3, .wav)")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["txt", "mp3", "wav"],
            help="Upload a text file with meeting content or an audio file for transcription"
        )
        
        if uploaded_file:
            # Validate file
            if not validate_file_size(uploaded_file):
                st.error("❌ File size must be less than 25MB")
                st.stop()
            
            if not validate_file_type(uploaded_file):
                st.error("❌ File type not supported. Please upload .txt, .mp3, or .wav files only")
                st.stop()
            
            file_name = uploaded_file.name
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            st.success(f"✅ File ready: {file_name} ({file_size_mb:.1f} MB)")
            
            # Handle text files
            if uploaded_file.name.lower().endswith('.txt'):
                try:
                    # Read content
                    content_bytes = uploaded_file.read()
                    content = content_bytes.decode('utf-8')
                    uploaded_file.seek(0)  # Reset file pointer for later use
                    
                    if len(content.strip()) == 0:
                        st.warning("⚠️ The text file appears to be empty")
                        st.stop()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Words", f"{len(content.split()):,}")
                    with col2:
                        prediction = predict_meeting_type(content)
                        st.metric("Predicted Type", prediction['predicted_type'].title())
                    
                    with st.expander("📄 Content Preview"):
                        preview = content[:800] + "..." if len(content) > 800 else content
                        st.text_area("", preview, height=150, disabled=True)
                        
                except UnicodeDecodeError:
                    st.error("❌ Cannot read file - please ensure it's a valid UTF-8 text file")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
                    st.stop()
            
            # Handle audio files
            elif uploaded_file.name.lower().endswith(('.mp3', '.wav')):
                st.info("🎵 Audio file will be transcribed automatically by the N8N workflow")
                content = "AUDIO_FILE"  # Marker for audio processing
    
    # Processing section
    if content or uploaded_file:
        st.subheader("🚀 Process Meeting Content")
        
        if st.button("🔄 Start Processing", type="primary", use_container_width=True):
            with st.spinner("Processing meeting content..."):
                # Add progress bar
                progress_bar = st.progress(0)
                
                # Determine processing type
                if content == "AUDIO_FILE" or (uploaded_file and uploaded_file.name.lower().endswith(('.mp3', '.wav'))):
                    progress_bar.progress(25)
                    result = send_audio_to_n8n(uploaded_file, meeting_title, attendees, n8n_url)
                else:
                    progress_bar.progress(25)
                    result = send_text_to_n8n(content, file_name, meeting_title, attendees, n8n_url)
                
                progress_bar.progress(100)
                time.sleep(0.5)  # Brief pause for UX
            
            # Display results
            display_results(result)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        🧠 Smart Meeting Processor | Powered by N8N + AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()