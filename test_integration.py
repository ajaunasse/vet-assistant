#!/usr/bin/env python3
"""
Simple integration test script for NeuroVet application
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000/api/v1"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_session_creation():
    """Test session creation"""
    try:
        response = requests.post(f"{API_BASE}/sessions", timeout=10)
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data.get("session_id")
            print(f"✅ Session created: {session_id}")
            return session_id
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Session creation error: {e}")
        return None

def test_chat_interaction(session_id):
    """Test chat interaction with a sample veterinary case"""
    test_message = """
    Bonjour Dr. NeuroVet. J'ai un Golden Retriever de 8 ans qui présente des signes neurologiques depuis 2 jours.
    Le chien a des difficultés à marcher, semble désorienté, et j'ai observé des mouvements oculaires anormaux.
    Il tourne en rond et semble avoir perdu l'équilibre. Pas de convulsions observées.
    """
    
    try:
        payload = {"message": test_message}
        response = requests.post(
            f"{API_BASE}/sessions/{session_id}/chat", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            assessment = response.json()
            print("✅ Chat interaction successful")
            print("📋 Assessment preview:")
            print(f"   Assessment: {assessment.get('assessment', 'N/A')[:100]}...")
            print(f"   Differentials: {len(assessment.get('differentials', []))} conditions")
            print(f"   Confidence: {assessment.get('confidence_level', 'N/A')}")
            return True
        else:
            print(f"❌ Chat interaction failed: {response.status_code}")
            if response.text:
                print(f"   Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat interaction error: {e}")
        return False

def main():
    """Run integration tests"""
    print("🧪 Starting NeuroVet Integration Tests\n")
    
    # Test 1: Health check
    print("1. Testing API health...")
    if not test_health():
        print("\n❌ Backend not running. Please start with: ./start_backend.sh")
        return False
    
    # Test 2: Session creation
    print("\n2. Testing session creation...")
    session_id = test_session_creation()
    if not session_id:
        return False
    
    # Test 3: Chat interaction
    print("\n3. Testing chat interaction...")
    if not test_chat_interaction(session_id):
        return False
    
    print("\n✅ All integration tests passed!")
    print("\n🚀 To use the application:")
    print("   1. Backend: ./start_backend.sh")
    print("   2. Frontend: ./start_frontend.sh")
    print("   3. Open: http://localhost:3000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)