# Comprehensive Troubleshooting Guide
## Meeting Analysis System - Streamlit & N8N Integration

This guide provides step-by-step troubleshooting for the meeting analysis system that combines Streamlit file upload, N8N workflow processing, OpenAI analysis, Google Sheets integration, and Recall.ai meeting recording.

---

## Table of Contents
1. [Quick Diagnostics](#1-quick-diagnostics)
2. [Streamlit Application Issues](#2-streamlit-application-issues)
3. [Network Connectivity Problems](#3-network-connectivity-problems)
4. [N8N Workflow Execution Issues](#4-n8n-workflow-execution-issues)
5. [Authentication & Credentials](#5-authentication--credentials)
6. [File Upload & Validation Errors](#6-file-upload--validation-errors)
7. [OpenAI API Problems](#7-openai-api-problems)
8. [Google Sheets Integration Issues](#8-google-sheets-integration-issues)
9. [Recall.ai Integration Problems](#9-recallai-integration-problems)
10. [Advanced Debugging](#10-advanced-debugging)

---

## 1. Quick Diagnostics

### System Health Check Commands
Run these commands first to identify the general state of your system:

```bash
# Check Python and dependencies
python --version
pip list | grep -E "(streamlit|requests)"

# Test Streamlit installation
python -c "import streamlit; print('Streamlit OK')"
python -c "import requests; print('Requests OK')"

# Check if Streamlit app can start
cd /path/to/your/project
streamlit run streamlit_n8n_uploader.py --server.port 8501 --server.headless true &
sleep 5
curl -s http://localhost:8501 > /dev/null && echo "Streamlit started successfully" || echo "Streamlit failed to start"
pkill -f streamlit
```

### Common Error Patterns
| Error Pattern | Likely Cause | Quick Fix |
|--------------|--------------|-----------|
| `ModuleNotFoundError: No module named 'streamlit'` | Missing dependencies | `pip install -r requirements.txt` |
| `Connection error - check N8N URL` | Network/URL issue | Verify N8N webhook URL format |
| `Request timed out` | N8N processing too slow | Check N8N workflow execution |
| `HTTP error: 422` | Invalid request data | Check file format and size |
| `HTTP error: 500` | N8N internal error | Check N8N logs and node configurations |

---

## 2. Streamlit Application Issues

### Problem: Streamlit Won't Start

**Error Messages:**
```
streamlit: command not found
ModuleNotFoundError: No module named 'streamlit'
```

**Diagnostic Steps:**
```bash
# Check if streamlit is installed
pip show streamlit

# Check Python path
which python
python -m site

# Reinstall if needed
pip uninstall streamlit
pip install streamlit>=1.28.0
```

**Solution:**
```bash
# Install requirements
pip install -r requirements.txt

# Or install individually
pip install streamlit>=1.28.0 requests>=2.31.0

# Verify installation
streamlit --version
```

### Problem: File Upload Interface Not Working

**Symptoms:**
- File uploader not appearing
- Files not being recognized
- Upload button disabled

**Diagnostic Commands:**
```bash
# Check file permissions in project directory
ls -la /path/to/project/
ls -la /path/to/project/*.py

# Test file accessibility
python -c "
import os
print('Current directory:', os.getcwd())
print('Files:', os.listdir('.'))
print('streamlit_n8n_uploader.py exists:', os.path.exists('streamlit_n8n_uploader.py'))
"
```

**Common Solutions:**
1. **File permissions**: `chmod 644 streamlit_n8n_uploader.py`
2. **Working directory**: Ensure you're running from the correct directory
3. **Port conflicts**: Use different port with `streamlit run app.py --server.port 8502`

### Problem: Application Crashes on File Upload

**Error Patterns:**
```python
UnicodeDecodeError: 'utf-8' codec can't decode byte
AttributeError: 'NoneType' object has no attribute 'size'
```

**Debug Commands:**
```bash
# Test with example files
echo "Test content" > test.txt
echo "Invalid binary content" | xxd -r -p > test_binary.txt

# Run with verbose logging
streamlit run streamlit_n8n_uploader.py --logger.level debug
```

**Code-Level Debugging:**
Add these debug lines to `streamlit_n8n_uploader.py`:

```python
# After line 87 (if uploaded_file is not None:)
st.write(f"Debug - File object: {type(uploaded_file)}")
st.write(f"Debug - File size: {uploaded_file.size if uploaded_file else 'None'}")
st.write(f"Debug - File type: {uploaded_file.type if uploaded_file else 'None'}")
```

---

## 3. Network Connectivity Problems

### Problem: Cannot Connect to N8N Webhook

**Error Messages:**
```
Connection error - check N8N URL
requests.exceptions.ConnectionError
```

**Diagnostic Steps:**
```bash
# Test basic connectivity
ping your-n8n-domain.com

# Test HTTP connectivity
curl -v https://your-n8n-instance.com/webhook/your-webhook-id

# Test with sample data
curl -X POST https://your-n8n-instance.com/webhook/your-webhook-id \
  -F "file=@test.txt" \
  -F "meetingType=test" \
  -F "meetingNotes=test notes"

# Check DNS resolution
nslookup your-n8n-domain.com
dig your-n8n-domain.com
```

**Common URL Format Issues:**
- **Correct**: `https://app.n8n.cloud/webhook/8204ed7a-b7e0-49e3-81b5-6383feaf2a65`
- **Incorrect**: `http://n8n-instance/webhook/` (missing webhook ID)
- **Incorrect**: `https://n8n-instance/api/webhook/` (wrong path)

### Problem: SSL/TLS Certificate Issues

**Error Messages:**
```
requests.exceptions.SSLError
certificate verify failed
```

**Solutions:**
```python
# Temporary fix (NOT for production)
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# In send_to_n8n function, modify the requests call:
response = requests.post(n8n_url, files=files, timeout=60, verify=False)
```

**Better Solution:**
```bash
# Update certificates
sudo apt-get update && sudo apt-get install ca-certificates
# or on macOS
brew install ca-certificates
```

---

## 4. N8N Workflow Execution Issues

### Problem: Webhook Not Triggering Workflow

**Diagnostic Steps:**
1. **Check N8N Webhook URL:**
   ```bash
   # Test webhook directly
   curl -X POST https://your-n8n.com/webhook/8204ed7a-b7e0-49e3-81b5-6383feaf2a65 \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
   ```

2. **Verify Workflow Status:**
   - Go to N8N interface
   - Check if workflow is **Active** (toggle switch should be ON)
   - Look for execution history in the workflow

3. **Test Individual Nodes:**
   - Click on each node in N8N
   - Use "Test step" to verify data flow
   - Check node configuration settings

### Problem: Workflow Fails at Validation Node

**Node:** `✅ Validate Input`
**Common Issues:**
- Missing `meetingType` or `meetingNotes` in input data
- Data format mismatch

**Fix in Streamlit App:**
Modify the `send_to_n8n` function to include required fields:

```python
def send_to_n8n(file, n8n_url: str, file_type: str, meeting_type="general") -> dict:
    try:
        # Ensure required fields are present
        form_data = {
            'meetingType': meeting_type,
            'meetingNotes': 'File upload from Streamlit app',
            'attendees': 'System'
        }
        
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(n8n_url, files=files, data=form_data, timeout=60)
        # ... rest of function
```

### Problem: JavaScript Code Nodes Failing

**Node:** `🔧 Prepare Sheet Data`
**Error Patterns:**
```
ReferenceError: $input is not defined
TypeError: Cannot read property 'json' of undefined
```

**Debug Steps:**
1. **Check Input Data Structure:**
   - Add console.log statements in the JavaScript code
   - Verify data is reaching the node

2. **Test JavaScript Logic:**
   ```javascript
   // Add at start of JS node
   console.log('Input items count:', $input.all().length);
   console.log('First item:', JSON.stringify($input.first().json, null, 2));
   ```

---

## 5. Authentication & Credentials

### Problem: Google Sheets Authentication Failed

**Error Messages:**
```
Invalid credentials
Authentication failed
403 Forbidden
```

**Diagnostic Steps:**
```bash
# Check if service account file exists
ls -la /path/to/service-account.json

# Verify JSON structure
python -c "
import json
with open('service-account.json') as f:
    data = json.load(f)
    print('Service account email:', data.get('client_email'))
    print('Project ID:', data.get('project_id'))
"
```

**Solution Steps:**
1. **Create/Update Service Account:**
   - Go to Google Cloud Console
   - Enable Google Sheets API
   - Create service account with Editor role
   - Download JSON key file

2. **Share Google Sheet:**
   - Open your Google Sheet
   - Share with service account email (found in JSON file)
   - Give "Editor" permissions

3. **Update N8N Credentials:**
   - Go to N8N → Settings → Credentials
   - Add/update Google Sheets credentials
   - Upload the service account JSON file

### Problem: OpenAI API Authentication

**Error Messages:**
```
Invalid API key
Rate limit exceeded
Quota exceeded
```

**Diagnostic Commands:**
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY" \
  | jq '.data[0].id'

# Check usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Solutions:**
1. **Invalid API Key:**
   - Verify key format: `sk-...` (starts with sk-)
   - Regenerate key in OpenAI dashboard
   - Update in N8N credentials

2. **Rate Limits:**
   - Add retry logic in N8N workflow
   - Implement exponential backoff
   - Consider upgrading OpenAI plan

### Problem: Recall.ai Authentication

**Error in HTTP Request Node:**
```
401 Unauthorized
Invalid API key
```

**Fix:**
1. **Get Valid API Key:**
   - Login to Recall.ai dashboard
   - Generate new API key

2. **Update N8N HTTP Request:**
   ```json
   {
     "name": "Authorization",
     "value": "Token YOUR_RECALL_AI_API_KEY"
   }
   ```

---

## 6. File Upload & Validation Errors

### Problem: File Size Validation Issues

**Error:** `File size must be less than 25MB`

**Diagnostic Commands:**
```bash
# Check actual file size
ls -lh your_file.mp3
stat your_file.mp3

# Test with different file sizes
dd if=/dev/zero of=test_small.txt bs=1M count=1
dd if=/dev/zero of=test_large.txt bs=1M count=30
```

**Solutions:**
1. **Increase size limit** (modify line 18 in `streamlit_n8n_uploader.py`):
   ```python
   return file_size_mb < 50  # Increase to 50MB
   ```

2. **Add compression**:
   ```python
   import gzip
   
   def compress_file(file_content):
       return gzip.compress(file_content)
   ```

### Problem: File Type Not Supported

**Error:** File uploader not accepting your file type

**Solution:** Update accepted file types (lines 75, 82):
```python
# For text files
type=["txt", "csv", "log", "md"]

# For audio files  
type=["mp3", "wav", "m4a", "aac"]
```

### Problem: Unicode Decode Errors

**Error:** `UnicodeDecodeError: 'utf-8' codec can't decode byte`

**Fix:** Add encoding detection:
```python
import chardet

def read_file_with_encoding(file):
    content = file.read()
    encoding = chardet.detect(content)['encoding']
    return content.decode(encoding or 'utf-8', errors='replace')
```

---

## 7. OpenAI API Problems

### Problem: API Rate Limits

**Error Messages:**
```
Rate limit reached
Too Many Requests (429)
```

**Solutions:**
1. **Add retry logic in N8N:**
   ```javascript
   // In Code node before OpenAI call
   const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
   await delay(1000); // Wait 1 second
   ```

2. **Implement exponential backoff:**
   ```javascript
   async function callOpenAIWithRetry(prompt, maxRetries = 3) {
     for (let i = 0; i < maxRetries; i++) {
       try {
         // Make OpenAI call
         return await makeOpenAICall(prompt);
       } catch (error) {
         if (error.status === 429 && i < maxRetries - 1) {
           await delay(Math.pow(2, i) * 1000); // Exponential backoff
           continue;
         }
         throw error;
       }
     }
   }
   ```

### Problem: Invalid Model Configuration

**Error:** `The model 'gpt-4.1-nano' does not exist`

**Fix:** Update model ID in N8N OpenAI nodes:
- Replace `gpt-4.1-nano` with `gpt-3.5-turbo`
- Or use `gpt-4` if you have access

### Problem: Context Length Exceeded

**Error:** `This model's maximum context length is X tokens`

**Solution:** Truncate input in preparation nodes:
```javascript
// In prompt preparation code
const maxTokens = 3000; // Approximate token limit
const truncatedNotes = item.json.meetingNotes.substring(0, maxTokens * 4); // Rough estimate
```

---

## 8. Google Sheets Integration Issues

### Problem: Sheet Not Found

**Error:** `Unable to parse range: Sheet1!A1:Z`

**Solution:**
1. **Verify sheet name in N8N configuration**
2. **Check if sheets exist:**
   - `Meeting Input Log`
   - `Action Items`
   - `Executive Summary`

### Problem: Permission Denied

**Error:** `The caller does not have permission`

**Steps to Fix:**
1. **Share sheet with service account:**
   ```bash
   # Get service account email from JSON file
   cat service-account.json | jq -r '.client_email'
   ```
   
2. **Share sheet with this email address as Editor**

3. **Verify sheet ID in workflow:**
   - Replace `REPLACE_WITH_YOUR_GOOGLE_SHEETS_ID` with actual sheet ID
   - Sheet ID is in the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID/edit`

### Problem: Data Format Mismatch

**Error:** Values don't align with sheet columns

**Fix:** Ensure data preparation matches sheet headers:
```javascript
// In "🔧 Prep Action Items" node
items.push({
  json: {
    'Meeting Date': actionItem.meetingDate,      // Column A
    'Meeting Type': actionItem.meetingType,      // Column B
    'Action Item': actionItem.actionItem,        // Column C
    'Owner': actionItem.owner,                   // Column D
    'Due Date': actionItem.dueDate,             // Column E
    'Priority': actionItem.priority,             // Column F
    'Status': actionItem.status,                 // Column G
    'Follow-up Required': 'No',                  // Column H
    'Meeting ID': actionItem.meetingId           // Column I
  }
});
```

---

## 9. Recall.ai Integration Problems

### Problem: Bot Creation Failed

**Error in HTTP Request:**
```
400 Bad Request
Invalid meeting URL
```

**Diagnostic Steps:**
```bash
# Test Recall.ai API directly
curl -X POST https://us-west-2.recall.ai/api/v1/bot \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/abc-defg-hij",
    "recording_config": {
      "audio_mixed_mp3": {}
    }
  }'
```

**Common Solutions:**
1. **Valid Meeting URL Format:**
   - Google Meet: `https://meet.google.com/xxx-xxxx-xxx`
   - Zoom: `https://zoom.us/j/123456789`
   - Teams: `https://teams.microsoft.com/l/meetup-join/...`

2. **API Key Format:**
   - Should be just the key, not prefixed with "Bearer"
   - Update Authorization header: `Token YOUR_API_KEY`

### Problem: Recording Not Available

**Error:** `Recording not found` or timeout in Wait node

**Solutions:**
1. **Increase Wait Time:**
   - Default wait may be too short for longer meetings
   - Update Wait node timeout to 30+ minutes

2. **Add Recording Status Check:**
   ```javascript
   // Add before transcription
   const botId = $json.id;
   const checkRecording = async () => {
     const response = await fetch(`https://us-west-2.recall.ai/api/v1/bot/${botId}`, {
       headers: { 'Authorization': 'Token YOUR_API_KEY' }
     });
     const data = await response.json();
     return data.status_changes?.recording_finished;
   };
   ```

### Problem: Transcription Fails

**Error in OpenAI Transcription Node:**
```
Invalid audio format
File not found
```

**Fix:**
1. **Check Binary Data Path:**
   - Verify `binaryPropertyName` in transcription node
   - Should match Recall.ai response structure

2. **Add Audio Format Validation:**
   ```javascript
   // Before transcription
   if ($json.recording_config?.audio_mixed_mp3?.url) {
     // Download audio file first
     const audioResponse = await fetch($json.recording_config.audio_mixed_mp3.url);
     const audioBuffer = await audioResponse.arrayBuffer();
     return { audio: audioBuffer };
   }
   ```

---

## 10. Advanced Debugging

### Enable Comprehensive Logging

**Streamlit App Debug Mode:**
```bash
# Run with debug logging
STREAMLIT_LOGGER_LEVEL=debug streamlit run streamlit_n8n_uploader.py

# Or modify app to add logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add to functions:
logger.debug(f"Sending file: {file.name}, size: {file.size}")
```

**N8N Workflow Debugging:**
1. **Add Debug Nodes:**
   ```javascript
   // Add Code node after problematic nodes
   console.log('Data at this point:', JSON.stringify($input.all(), null, 2));
   return $input.all();
   ```

2. **Check Execution History:**
   - N8N → Executions
   - Click on failed executions
   - Review error details and data flow

### Network Traffic Analysis

**Capture HTTP Requests:**
```bash
# Monitor outgoing requests
sudo tcpdump -i any -s 0 -A 'host your-n8n-domain.com'

# Or use mitmproxy for detailed analysis
pip install mitmproxy
mitmproxy --port 8080
```

**Set Proxy in Python:**
```python
import requests

proxies = {
    'http': 'http://localhost:8080',
    'https': 'http://localhost:8080',
}

# In send_to_n8n function:
response = requests.post(n8n_url, files=files, timeout=60, proxies=proxies, verify=False)
```

### Performance Monitoring

**Add Timing to Streamlit App:**
```python
import time

def send_to_n8n(file, n8n_url: str, file_type: str) -> dict:
    start_time = time.time()
    try:
        # ... existing code ...
        response = requests.post(n8n_url, files=files, timeout=60)
        end_time = time.time()
        
        return {
            "success": True,
            "status_code": response.status_code,
            "message": "File uploaded successfully",
            "response": response.text if response.text else "No response content",
            "processing_time": end_time - start_time
        }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False, 
            "error": f"Error after {end_time - start_time:.2f}s: {str(e)}"
        }
```

### Database/Storage Debugging

**Test Google Sheets Connection:**
```python
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def test_sheets_connection():
    credentials = Credentials.from_service_account_file('service-account.json')
    service = build('sheets', 'v4', credentials=credentials)
    
    # Test read
    sheet_id = 'YOUR_SHEET_ID'
    result = service.spreadsheets().values().get(
        spreadsheetId=sheet_id, range='Sheet1!A1:A1'
    ).execute()
    
    print('Connection successful:', result.get('values'))
```

### Emergency Recovery Procedures

**If Workflow is Completely Broken:**
1. **Backup current workflow:**
   ```bash
   curl -X GET "https://your-n8n.com/api/v1/workflows/YOUR_WORKFLOW_ID" \
     -H "Authorization: Bearer YOUR_API_TOKEN" > workflow_backup.json
   ```

2. **Reset to minimal working state:**
   - Create simple webhook → response workflow
   - Test basic connectivity
   - Add nodes one by one

3. **Gradual restoration:**
   - Import one node type at a time
   - Test after each addition
   - Monitor execution logs

**If Streamlit App Won't Start:**
```bash
# Nuclear option - clean Python environment
pip freeze > requirements_backup.txt
pip uninstall -y -r requirements_backup.txt
pip install streamlit requests

# Test minimal app
cat > minimal_test.py << EOF
import streamlit as st
st.write("Hello World")
EOF

streamlit run minimal_test.py
```

---

## Emergency Contacts & Resources

- **Streamlit Documentation**: https://docs.streamlit.io/
- **N8N Documentation**: https://docs.n8n.io/
- **OpenAI API Status**: https://status.openai.com/
- **Google Cloud Status**: https://status.cloud.google.com/
- **Recall.ai Status**: Check their status page or contact support

---

## Conclusion

This troubleshooting guide covers the most common issues you'll encounter with the meeting analysis system. Always start with the quick diagnostics, then work through the specific sections relevant to your problem. Remember to check logs, verify configurations, and test individual components before assuming the entire system is broken.

For persistent issues not covered here, gather the following information:
- Error messages (exact text)
- System specifications
- Configuration files
- Execution logs
- Network conditions

This information will help in further diagnosis and resolution.