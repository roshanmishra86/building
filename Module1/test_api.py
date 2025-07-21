import requests
import json

def test_meeting_api():
    """Test the meeting API with a simple standup"""
    
    payload = {
        "meeting_type": "standup",
        "meeting_notes": """
        Daily standup for Sprint 23.
        
        John: Completed user auth feature, now working on API integration.
        Sarah: Finished database updates, starting frontend components today.
        Mike: Blocked on third-party integration - waiting for API keys.
        
        Next standup tomorrow 9 AM.
        """,
        "attendees": "John Smith, Sarah Johnson, Mike Chen"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/meeting/analyse",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_meeting_api()
