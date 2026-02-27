"""
Test script to check available Gemini models with your API key
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in .env file")
    exit(1)

print(f"[INFO] API Key found: {api_key[:20]}...")
print()

# Configure Gemini
genai.configure(api_key=api_key)

print("=" * 60)
print("AVAILABLE GEMINI MODELS")
print("=" * 60)

try:
    # List all available models
    models = genai.list_models()
    
    gemini_models = []
    for model in models:
        # Filter for Gemini models that support generateContent
        if 'generateContent' in model.supported_generation_methods:
            gemini_models.append(model)
            print(f"\nModel: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Input Token Limit: {model.input_token_limit:,}")
            print(f"  Output Token Limit: {model.output_token_limit:,}")
            print(f"  Supported Methods: {', '.join(model.supported_generation_methods)}")
    
    print()
    print("=" * 60)
    print(f"TOTAL MODELS AVAILABLE: {len(gemini_models)}")
    print("=" * 60)
    
    # Test each model with a simple query
    print("\n" + "=" * 60)
    print("TESTING MODELS")
    print("=" * 60)
    
    test_prompt = "Say 'Hello' in one word only."
    
    # Test specific models
    test_models = [
        'gemini-3-flash-preview',
        'gemini-2.0-flash-exp',
        'gemini-1.5-flash',
        'gemini-1.5-flash-8b',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    for model_name in test_models:
        try:
            print(f"\n[TEST] {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_prompt)
            print(f"  [OK] Response: {response.text.strip()}")
        except Exception as e:
            print(f"  [FAILED] {str(e)}")
    
    print()
    print("=" * 60)
    print("RECOMMENDED MODELS FOR YOUR PROJECT")
    print("=" * 60)
    print()
    print("1. gemini-3-flash-preview (RECOMMENDED)")
    print("   - Latest Gemini 3 model (Preview)")
    print("   - FREE tier available")
    print("   - Pro-level intelligence at Flash speed")
    print("   - 1M token context window")
    print("   - Released: December 17, 2025")
    print()
    print("2. gemini-2.0-flash-exp")
    print("   - Experimental Gemini 2 model")
    print("   - FREE tier available")
    print("   - Good for testing")
    print()
    print("3. gemini-1.5-flash")
    print("   - Stable production model")
    print("   - FREE tier available")
    print("   - Good balance of speed and quality")
    print()
    print("4. gemini-1.5-flash-8b")
    print("   - Lightweight model")
    print("   - FREE tier available")
    print("   - Fastest response time")
    print()
    print("5. gemini-1.5-pro")
    print("   - Most capable Gemini 1.5 model")
    print("   - FREE tier available (lower limits)")
    print("   - Best for complex analysis")
    print()
    print("NOTE: Model ID is 'gemini-3-flash-preview' (not 3.0 or 3.1)")
    print("      Source: https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-flash")
    print()

except Exception as e:
    print(f"[ERROR] Failed to list models: {e}")
    import traceback
    traceback.print_exc()
