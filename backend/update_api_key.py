"""
Quick API Key Updater
Run this script to update your Gemini API key in .env file
"""

import os

print("=" * 60)
print("GEMINI API KEY UPDATER")
print("=" * 60)
print()
print("IMPORTANT: Get a BRAND NEW key from:")
print("https://aistudio.google.com/app/apikey")
print()
print("Steps:")
print("1. DELETE the old leaked key")
print("2. Click 'Create API Key'")
print("3. Copy the NEW key")
print("4. Paste it below")
print()
print("=" * 60)
print()

# Get new API key from user
new_key = input("Paste your NEW Gemini API key here: ").strip()

if not new_key or len(new_key) < 30:
    print()
    print("[ERROR] Invalid API key. Please try again.")
    exit(1)

# Path to .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')

# Read current .env
with open(env_path, 'r') as f:
    lines = f.readlines()

# Update all Gemini keys
updated_lines = []
for line in lines:
    if line.startswith('GEMINI_API_KEY_3_FLASH='):
        updated_lines.append(f'GEMINI_API_KEY_3_FLASH={new_key}\n')
    elif line.startswith('GEMINI_API_KEY_2_5_FLASH_1='):
        updated_lines.append(f'GEMINI_API_KEY_2_5_FLASH_1={new_key}\n')
    elif line.startswith('GEMINI_API_KEY_2_5_FLASH_2='):
        updated_lines.append(f'GEMINI_API_KEY_2_5_FLASH_2={new_key}\n')
    else:
        updated_lines.append(line)

# Write back
with open(env_path, 'w') as f:
    f.writelines(updated_lines)

print()
print("=" * 60)
print("[SUCCESS] API key updated in .env file!")
print("=" * 60)
print()
print("Next steps:")
print("1. Restart the backend server")
print("2. Test with: python test_gemini_key.py")
print("3. If test passes, restart InsightX app")
print()
