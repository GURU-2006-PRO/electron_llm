"""
Diagnose API Key Issues
Tests if your current API keys are working
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

print("=" * 70)
print("API KEY DIAGNOSTICS")
print("=" * 70)
print()

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"[1/4] Loading .env from: {env_path}")
print(f"      File exists: {os.path.exists(env_path)}")
load_dotenv(env_path)
print()

# Check keys
print("[2/4] Checking API keys in .env file...")
keys = {
    'GEMINI_API_KEY_3_FLASH': os.getenv('GEMINI_API_KEY_3_FLASH'),
    'GEMINI_API_KEY_2_5_FLASH_1': os.getenv('GEMINI_API_KEY_2_5_FLASH_1'),
    'GEMINI_API_KEY_2_5_FLASH_2': os.getenv('GEMINI_API_KEY_2_5_FLASH_2'),
    'OPENROUTER_API_KEY': os.getenv('OPENROUTER_API_KEY')
}

for key_name, key_value in keys.items():
    if key_value and key_value.strip():
        print(f"  ✓ {key_name}: {key_value[:20]}... (SET)")
    else:
        print(f"  ✗ {key_name}: NOT SET")
print()

# Test Gemini keys
print("[3/4] Testing Gemini API keys...")
gemini_keys_to_test = [
    ('GEMINI_API_KEY_3_FLASH', keys['GEMINI_API_KEY_3_FLASH']),
    ('GEMINI_API_KEY_2_5_FLASH_1', keys['GEMINI_API_KEY_2_5_FLASH_1']),
    ('GEMINI_API_KEY_2_5_FLASH_2', keys['GEMINI_API_KEY_2_5_FLASH_2'])
]

working_keys = []
blocked_keys = []

for key_name, key_value in gemini_keys_to_test:
    if not key_value or not key_value.strip():
        print(f"  ⊘ {key_name}: SKIPPED (not set)")
        continue
    
    try:
        genai.configure(api_key=key_value)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content("Say 'OK' if you can read this")
        
        if response and response.text:
            print(f"  ✓ {key_name}: WORKING")
            working_keys.append(key_name)
        else:
            print(f"  ✗ {key_name}: FAILED (no response)")
            blocked_keys.append(key_name)
    except Exception as e:
        error_str = str(e)
        if '403' in error_str or 'leaked' in error_str.lower():
            print(f"  ✗ {key_name}: BLOCKED (key was leaked/reported)")
            blocked_keys.append(key_name)
        elif '429' in error_str or 'quota' in error_str.lower():
            print(f"  ⚠ {key_name}: QUOTA EXCEEDED (but key is valid)")
            working_keys.append(key_name)
        else:
            print(f"  ✗ {key_name}: ERROR - {error_str[:60]}")
            blocked_keys.append(key_name)
print()

# Summary
print("[4/4] SUMMARY")
print("=" * 70)
if working_keys:
    print(f"✓ Working keys: {len(working_keys)}")
    for key in working_keys:
        print(f"  - {key}")
    print()

if blocked_keys:
    print(f"✗ Blocked/Failed keys: {len(blocked_keys)}")
    for key in blocked_keys:
        print(f"  - {key}")
    print()
    print("SOLUTION:")
    print("  1. Go to: https://aistudio.google.com/app/apikey")
    print("  2. DELETE the old API keys (they were leaked)")
    print("  3. CREATE NEW API keys")
    print("  4. Update backend/.env file with NEW keys")
    print("  5. NEVER share API keys in screenshots or chat!")
    print()

if not working_keys and not blocked_keys:
    print("✗ No API keys configured")
    print()
    print("SOLUTION:")
    print("  1. Go to: https://aistudio.google.com/app/apikey")
    print("  2. Create NEW API keys")
    print("  3. Add them to backend/.env file")
    print()

print("=" * 70)
