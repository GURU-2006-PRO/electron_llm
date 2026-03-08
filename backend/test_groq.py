"""
Test Groq API connectivity
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

print("=" * 60)
print("GROQ API KEY TESTER")
print("=" * 60)

if not GROQ_API_KEY:
    print("[ERROR] GROQ_API_KEY not found in .env file")
    print("[INFO] Please add your Groq API key to .env")
    exit(1)

print(f"[INFO] Testing Groq key: {GROQ_API_KEY[:20]}...")

try:
    # Initialize Groq client
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )
    
    print("[INFO] Sending test query to Groq Llama 3.3 70B...")
    
    # Test query
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": "Say 'Groq is working!' if you can read this."
            }
        ],
        max_tokens=50,
        temperature=0.7
    )
    
    answer = response.choices[0].message.content
    
    print("=" * 60)
    print("[SUCCESS] GROQ IS WORKING!")
    print("=" * 60)
    print("Response from Groq Llama 3.3 70B:")
    print("-" * 60)
    print(answer)
    print("-" * 60)
    print("[OK] Your Groq key is working!")
    print("[OK] You can now use Groq models in InsightX Analytics")
    
except Exception as e:
    print("=" * 60)
    print("[ERROR] GROQ API FAILED")
    print("=" * 60)
    print(f"Error: {str(e)}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. Network connectivity issue")
    print("3. Groq API service down")
    print("\nGet a new key at: https://console.groq.com/keys")
