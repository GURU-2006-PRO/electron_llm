"""
Test if backend can start
"""
print("=" * 60)
print("TESTING BACKEND STARTUP")
print("=" * 60)

try:
    print("[1/5] Testing imports...")
    from flask import Flask
    print("  ✓ Flask OK")
    
    import pandas as pd
    print("  ✓ Pandas OK")
    
    from dotenv import load_dotenv
    print("  ✓ dotenv OK")
    
    import google.generativeai as genai
    print("  ✓ Google AI OK")
    
    print()
    print("[2/5] Testing .env loading...")
    import os
    load_dotenv()
    gemini_key = os.getenv('GEMINI_API_KEY_3_FLASH')
    print(f"  GEMINI_API_KEY_3_FLASH: {gemini_key[:20] if gemini_key else 'NOT SET'}...")
    
    print()
    print("[3/5] Testing api_server import...")
    import api_server
    print("  ✓ api_server imported")
    
    print()
    print("[4/5] Checking Flask app...")
    print(f"  Flask app: {api_server.app}")
    
    print()
    print("[5/5] Checking LLM service...")
    print(f"  llm_service: {api_server.llm_service}")
    print(f"  gemini_manager: {api_server.gemini_manager}")
    
    print()
    print("=" * 60)
    print("ALL CHECKS PASSED!")
    print("=" * 60)
    print()
    print("Backend should be able to start.")
    print("Run: python api_server.py")
    
except Exception as e:
    print()
    print("=" * 60)
    print("ERROR FOUND!")
    print("=" * 60)
    print(f"\n{e}\n")
    import traceback
    traceback.print_exc()
