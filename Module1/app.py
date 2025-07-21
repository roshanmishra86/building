from flask import Flask, request, jsonify
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import requests
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://your-n8n-instance.com/webhook/meeting-intelligence-webhook')

@dataclass
class MeetingRequest:
    """Domain model for meeting analysis requests"""
    meeting_type: str
    meeting_notes: str
    attendees: str
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the meeting request"""
        if not self.meeting_type or not self.meeting_type.strip():
            return False, "Meeting type is required"
        
        if not self.meeting_notes or not self.meeting_notes.strip():
            return False, "Meeting notes are required"
        
        if len(self.meeting_notes.strip()) < 20:
            return False, "Meeting notes too short"
        
        valid_types = ['standup', 'strategy', 'client', 'general']
        if self.meeting_type.lower() not in valid_types:
            return False, f"Meeting type must be one of: {', '.join(valid_types)}"
        
        return True, None
    
    def to_webhook_payload(self) -> Dict[str, Any]:
        """Convert to n8n webhook payload format"""
        return {
            'meetingType': self.meeting_type.lower(),
            'meetingNotes': self.meeting_notes.strip(),
            'attendees': self.attendees.strip() if self.attendees else 'Not specified'
        }

@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/meeting/analyse', methods=['POST'])
def analyse_meeting():
    """Analyse meeting notes using n8n workflow"""
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON payload required'}), 400
        
        # Create meeting request
        meeting_request = MeetingRequest(
            meeting_type=data.get('meeting_type', ''),
            meeting_notes=data.get('meeting_notes', ''),
            attendees=data.get('attendees', '')
        )
        
        # Validate
        is_valid, error_message = meeting_request.validate()
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Send to n8n webhook
        payload = meeting_request.to_webhook_payload()
        logger.info(f"Sending {meeting_request.meeting_type} meeting to n8n")
        
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'message': 'Meeting analysis started',
                'webhook_response': response.text
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Webhook failed with status {response.status_code}',
                'details': response.text
            }), 400
            
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({'error': 'Failed to reach n8n webhook'}), 502
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'error': 'Something went wrong'}), 500

@app.route('/meeting/types', methods=['GET'])
def get_meeting_types():
    """Get supported meeting types"""
    return jsonify({
        'types': ['standup', 'strategy', 'client', 'general'],
        'example_payload': {
            'meeting_type': 'standup',
            'meeting_notes': 'Your meeting notes here...',
            'attendees': 'John, Sarah, Mike'
        }
    })

if __name__ == '__main__':
    if N8N_WEBHOOK_URL == 'https://roshanmishra.app.n8n.cloud/webhook-test/meeting-notes':
        print("⚠️  Set N8N_WEBHOOK_URL environment variable")
    
    print(f"🚀 Starting API server...")
    print(f"📡 N8N Webhook: {N8N_WEBHOOK_URL}")
    app.run(debug=True, host='0.0.0.0', port=5000)