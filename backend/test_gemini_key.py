"""
Simple Gemini API Key Tester
Paste your API key below and run this script to test if it works
"""

import google.generativeai as genai

# ============================================
# PASTE YOUR GEMINI API KEY HERE
# ============================================
GEMINI_API_KEY = "AIzaSyCWPhvSSAXMqi_Th-b7kH6IDQVTO4igI6U"
# ============================================

def test_gemini_key():
    """Test if the Gemini API key is valid and working"""
    
    print("=" * 60)
    print("GEMINI API KEY TESTER")
    print("=" * 60)
    print()
    
    if not GEMINI_API_KEY or GEMINI_API_KEY == "paste-your-key-here":
        print("[ERROR] Please paste your API key in the script first!")
        print("Edit this file and replace 'paste-your-key-here' with your actual key")
        return
    
    print(f"[INFO] Testing API key: {GEMINI_API_KEY[:20]}...")
    print()
    
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create model - using Gemini 3.0 Flash (latest)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        print("[INFO] Sending test query to Gemini...")
        
        # Send a simple test query
        response = model.generate_content("Say 'Hello! API key is working!' in one sentence.")
        
        print()
        print("=" * 60)
        print("[SUCCESS] API KEY IS VALID AND WORKING!")
        print("=" * 60)
        print()
        print("Response from Gemini:")
        print("-" * 60)
        print(response.text)
        print("-" * 60)
        print()
        print("[OK] Your API key is working correctly!")
        print("[OK] You can now use this key in InsightX Analytics")
        print()
        
    except Exception as e:
        error_msg = str(e)
        print()
        print("=" * 60)
        print("[ERROR] API KEY TEST FAILED!")
        print("=" * 60)
        print()
        print(f"Error: {error_msg}")
        print()
        
        # Provide specific guidance based on error
        if "403" in error_msg or "API_KEY_INVALID" in error_msg:
            print("[SOLUTION] Your API key is invalid or has been blocked.")
            print("1. Go to: https://aistudio.google.com/app/apikey")
            print("2. Delete this key if it exists")
            print("3. Create a NEW API key")
            print("4. Paste the new key in this script and run again")
            
        elif "429" in error_msg or "quota" in error_msg.lower():
            print("[SOLUTION] API quota exceeded.")
            print("1. Wait 24 hours for quota to reset, OR")
            print("2. Create a new API key at: https://aistudio.google.com/app/apikey")
            
        elif "leaked" in error_msg.lower():
            print("[SOLUTION] Your API key was reported as leaked!")
            print("1. Go to: https://aistudio.google.com/app/apikey")
            print("2. DELETE this key immediately")
            print("3. Create a NEW API key")
            print("4. NEVER share the new key in screenshots or chat")
            
        else:
            print("[SOLUTION] Unknown error. Check your internet connection.")
            print("If problem persists, create a new API key at:")
            print("https://aistudio.google.com/app/apikey")
        
        print()

if __name__ == "__main__":
    test_gemini_key()
