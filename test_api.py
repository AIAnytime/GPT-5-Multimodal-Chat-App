#!/usr/bin/env python3
"""
Test script for GPT-5 Multimodal API
This script demonstrates how to use all the API endpoints
"""

import requests
import json
import base64
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test the root endpoint"""
    print("🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_presets_endpoint():
    """Test the presets endpoint"""
    print("🔍 Testing presets endpoint...")
    response = requests.get(f"{BASE_URL}/presets")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_text_chat():
    """Test text-only chat"""
    print("🔍 Testing text chat endpoint...")
    
    data = {
        "message": "Hello! Can you tell me a short joke?",
        "conversation_history": []
    }
    
    response = requests.post(f"{BASE_URL}/chat/text", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response']}")
        print(f"Conversation length: {len(result['conversation_history'])}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_image_base64_chat():
    """Test image analysis with base64 encoded image"""
    print("🔍 Testing image base64 chat endpoint...")
    
    # Create a simple test image (1x1 pixel PNG)
    # This is just for testing - replace with actual image data
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    data = {
        "image_base64": test_image_b64,
        "prompt": "What do you see in this image?",
        "preset_action": None
    }
    
    response = requests.post(f"{BASE_URL}/chat/image-base64", json=data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response']}")
        print(f"Analysis type: {result['analysis_type']}")
    else:
        print(f"Error: {response.text}")
    print("-" * 50)

def test_preset_actions():
    """Test preset actions with image"""
    print("🔍 Testing preset actions...")
    
    # Simple test image
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    presets = ["analyze", "summarize", "describe"]
    
    for preset in presets:
        print(f"Testing preset: {preset}")
        data = {
            "image_base64": test_image_b64,
            "preset_action": preset
        }
        
        response = requests.post(f"{BASE_URL}/chat/image-base64", json=data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['response'][:100]}...")
        else:
            print(f"Error: {response.text}")
        print()

def main():
    """Run all tests"""
    print("🚀 Starting GPT-5 Multimodal API Tests")
    print("=" * 60)
    
    try:
        test_root_endpoint()
        test_presets_endpoint()
        test_text_chat()
        test_image_base64_chat()
        test_preset_actions()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python3 main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
