"""
DeepSeek R1 API Key Tester
Test if your OpenRouter key works with DeepSeek R1
"""

from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

print("=" * 60)
print("DEEPSEEK R1 API KEY TESTER")
print("=" * 60)
print()

if not OPENROUTER_API_KEY:
    print("[ERROR] OPENROUTER_API_KEY not found in .env file!")
    print("Please add your OpenRouter API key to backend/.env")
    exit(1)

print(f"[INFO] Testing OpenRouter key: {OPENROUTER_API_KEY[:20]}...")
print()

try:
    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    
    print("[INFO] Sending test query to DeepSeek R1...")
    print()
    
    # Test with DeepSeek R1
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {"role": "user", "content": "Say 'DeepSeek R1 is working!' in one sentence."}
        ]
    )
    
    result = response.choices[0].message.content
    
    print("=" * 60)
    print("[SUCCESS] DEEPSEEK R1 IS WORKING!")
    print("=" * 60)
    print()
    print("Response from DeepSeek R1:")
    print("-" * 60)
    print(result)
    print("-" * 60)
    print()
    print("[OK] Your OpenRouter key is working with DeepSeek R1!")
    print("[OK] You can now use DeepSeek R1 in InsightX Analytics")
    print()
    
except Exception as e:
    error_msg = str(e)
    print()
    print("=" * 60)
    print("[ERROR] DEEPSEEK R1 TEST FAILED!")
    print("=" * 60)
    print()
    print(f"Error: {error_msg}")
    print()
    
    if "401" in error_msg or "authentication" in error_msg.lower():
        print("[SOLUTION] Your OpenRouter API key is invalid.")
        print("1. Go to: https://openrouter.ai/keys")
        print("2. Create a new API key")
        print("3. Update OPENROUTER_API_KEY in backend/.env")
        
    elif "402" in error_msg or "credits" in error_msg.lower():
        print("[SOLUTION] Your OpenRouter account has no credits.")
        print("1. Go to: https://openrouter.ai/credits")
        print("2. Add credits to your account")
        print("3. Try again")
        
    elif "429" in error_msg or "rate limit" in error_msg.lower():
        print("[SOLUTION] Rate limit exceeded.")
        print("Wait a few minutes and try again.")
        
    else:
        print("[SOLUTION] Unknown error. Check:")
        print("1. Internet connection")
        print("2. OpenRouter API status: https://status.openrouter.ai")
        print("3. Your API key at: https://openrouter.ai/keys")
    
    print()
