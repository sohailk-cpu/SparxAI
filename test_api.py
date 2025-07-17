#!/usr/bin/env python3
"""
Test script for the AI Story Generator FastAPI backend.
This script demonstrates the main API functionality.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("🚀 Testing AI Story Generator FastAPI Backend")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 2: User registration
    print("\n2. Testing user registration...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   Created user: {user_data['username']} (ID: {user_data['id']})")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return
    
    # Test 3: User login
    print("\n3. Testing user login...")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ User login successful")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   Token type: {token_data['token_type']}")
            print(f"   Token: {access_token[:50]}...")
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ User login error: {e}")
        return
    
    # Set up headers for authenticated requests
    auth_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test 4: Get user info
    print("\n4. Testing get user info...")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=auth_headers)
        if response.status_code == 200:
            print("✅ Get user info successful")
            user_info = response.json()
            print(f"   User: {user_info['username']} ({user_info['email']})")
        else:
            print(f"❌ Get user info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get user info error: {e}")
    
    # Test 5: Create a story
    print("\n5. Testing story creation...")
    story_data = {
        "title": "Test Adventure Story",
        "prompt": "A brave adventurer discovers a magical crystal in an ancient cave",
        "content": "In the depths of the forgotten cave, Sarah found a crystal that glowed with mysterious light. As she touched it, visions of ancient civilizations filled her mind, and she realized this was the key to unlocking the secrets of the past.",
        "genre": "fantasy",
        "is_public": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/stories",
            json=story_data,
            headers=auth_headers
        )
        if response.status_code in [200, 201]:
            print("✅ Story creation successful")
            story = response.json()
            story_id = story["id"]
            print(f"   Created story: '{story['title']}' (ID: {story_id})")
        else:
            print(f"❌ Story creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            story_id = None
    except Exception as e:
        print(f"❌ Story creation error: {e}")
        story_id = None
    
    # Test 6: List stories
    print("\n6. Testing story listing...")
    try:
        response = requests.get(f"{BASE_URL}/stories", headers=auth_headers)
        if response.status_code == 200:
            print("✅ Story listing successful")
            stories_data = response.json()
            print(f"   Found {stories_data['total']} stories")
            if stories_data['stories']:
                for story in stories_data['stories'][:3]:  # Show first 3
                    print(f"   - '{story['title']}' by {story.get('author', {}).get('username', 'Unknown')}")
        else:
            print(f"❌ Story listing failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Story listing error: {e}")
    
    # Test 7: Get specific story
    if story_id:
        print(f"\n7. Testing get specific story (ID: {story_id})...")
        try:
            response = requests.get(f"{BASE_URL}/stories/{story_id}", headers=auth_headers)
            if response.status_code == 200:
                print("✅ Get specific story successful")
                story = response.json()
                print(f"   Story: '{story['title']}'")
                print(f"   Content preview: {story['content'][:100]}...")
            else:
                print(f"❌ Get specific story failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Get specific story error: {e}")
    
    # Test 8: Get user's stories
    print("\n8. Testing get user's stories...")
    try:
        response = requests.get(f"{BASE_URL}/stories/user/me", headers=auth_headers)
        if response.status_code == 200:
            print("✅ Get user's stories successful")
            user_stories = response.json()
            print(f"   User has {len(user_stories)} stories")
        else:
            print(f"❌ Get user's stories failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get user's stories error: {e}")
    
    # Test 9: Story generation (Note: requires OpenAI API key)
    print("\n9. Testing story generation...")
    print("   ⚠️  Note: This requires a valid OpenAI API key in the environment")
    generation_data = {
        "prompt": "A robot discovers emotions for the first time",
        "genre": "science fiction",
        "max_tokens": 200,
        "temperature": 0.8
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/stories/generate",
            json=generation_data,
            headers=auth_headers
        )
        if response.status_code == 200:
            print("✅ Story generation successful")
            generated = response.json()
            print(f"   Generated content preview: {generated['generated_content'][:200]}...")
        else:
            print(f"❌ Story generation failed: {response.status_code}")
            if "openai" in response.text.lower():
                print("   💡 This is likely due to missing or invalid OpenAI API key")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Story generation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("\n📚 For more details, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()