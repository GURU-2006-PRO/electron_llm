"""
Fix Expired API Keys
Removes expired keys from .env file
"""
import os

env_path = os.path.join(os.path.dirname(__file__), '.env')

print("=" * 70)
print("FIXING EXPIRED API KEYS")
print("=" * 70)
print()

print(f"Reading .env from: {env_path}")
print()

# Read .env
with open(env_path, 'r') as f:
    lines = f.readlines()

# Update expired keys to empty
updated_lines = []
keys_cleared = []

for line in lines:
    # Clear the expired keys (keep the working one)
    if line.startswith('GEMINI_API_KEY_2_5_FLASH_1=') and 'AIzaSyB-iCQe8Hbx00xP9uNbXGt2IW0FIpSNqXI' in line:
        updated_lines.append('GEMINI_API_KEY_2_5_FLASH_1=\n')
        keys_cleared.append('GEMINI_API_KEY_2_5_FLASH_1')
        print("✓ Cleared GEMINI_API_KEY_2_5_FLASH_1 (expired)")
    elif line.startswith('GEMINI_API_KEY_2_5_FLASH_2=') and 'AIzaSyB-iCQe8Hbx00xP9uNbXGt2IW0FIpSNqXI' in line:
        updated_lines.append('GEMINI_API_KEY_2_5_FLASH_2=\n')
        keys_cleared.append('GEMINI_API_KEY_2_5_FLASH_2')
        print("✓ Cleared GEMINI_API_KEY_2_5_FLASH_2 (expired)")
    else:
        updated_lines.append(line)

# Write back
with open(env_path, 'w') as f:
    f.writelines(updated_lines)

print()
print("=" * 70)
print("DONE!")
print("=" * 70)
print()
print(f"Cleared {len(keys_cleared)} expired keys")
print()
print("Your working key (GEMINI_API_KEY_3_FLASH) is still active.")
print()
print("NEXT STEPS:")
print("  1. Start backend: python api_server.py")
print("  2. Start frontend: npm start")
print("  3. System will use your working Gemini key")
print()
print("OPTIONAL: Get more keys for fallback")
print("  1. Go to: https://aistudio.google.com/app/apikey")
print("  2. Create 2 NEW API keys")
print("  3. Add them to Settings UI in the app")
print()
print("=" * 70)
