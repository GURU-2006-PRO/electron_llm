"""
Test Gemini API to verify it works
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

print("=" * 50)
print("Testing Gemini API")
print("=" * 50)

if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-gemini-key-here':
    print("[ERROR] GEMINI_API_KEY not set in .env file")
    exit(1)

print(f"[OK] API Key found: {GEMINI_API_KEY[:20]}...")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# List available models
print("\n[INFO] Listing available models...")
try:
    models = genai.list_models()
    print("[OK] Available Gemini models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
except Exception as e:
    print(f"[ERROR] Failed to list models: {e}")
    exit(1)

# Test different model names
test_models = [
    'gemini-1.5-flash',
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro',
    'gemini-pro',
    'gemini-2.0-flash-exp'
]

print("\n[INFO] Testing model availability...")
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello'")
        print(f"[OK] {model_name} - WORKS ✅")
        print(f"     Response: {response.text[:50]}")
    except Exception as e:
        print(f"[FAIL] {model_name} - {str(e)[:80]}")

print("\n" + "=" * 50)
print("Test Complete")
print("=" * 50)
