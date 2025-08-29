import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Veterinary Neurological Diagnostic Assistant API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Veterinary Neurological Diagnostic Assistant" in data["message"]

def test_create_session():
    """Test session creation"""
    response = client.post("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0