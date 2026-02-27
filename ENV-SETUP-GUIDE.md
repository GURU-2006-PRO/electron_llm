# Environment Variables Setup Guide 🔐

## Overview

All API keys are now stored in `.env` file for security. This guide will help you set up your environment variables.

## Quick Setup

### Step 1: Install python-dotenv
```bash
cd insightx-app/backend
pip install python-dotenv
```

### Step 2: Your .env File is Ready!
The `.env` file has been created with your current API keys at:
```
insightx-app/backend/.env
```

### Step 3: Add More API Keys (Optional)
Edit `backend/.env` and add your keys:

```bash
# Open in text editor
notepad backend/.env  # Windows
nano backend/.env     # Linux/Mac
```

---

## Getting API Keys

### 1. Groq API (Recommended - FREE) ⭐⭐⭐⭐⭐

**Why:** 500K free tokens daily, fastest inference

**Steps:**
1. Go to https://console.groq.com/
2. Sign up (no credit card required)
3. Click "API Keys" in sidebar
4. Click "Create API Key"
5. Copy the key (starts with `gsk_...`)
6. Add to `.env`:
   ```
   GROQ_API_KEY=gsk_your_key_here
   ```

**Models Available:**
- Llama 3.3 70B (best for analytics)
- Llama 3.1 405B (best reasoning)
- Qwen 2.5 72B
- DeepSeek V3
- Mixtral 8x7B

---

### 2. Together AI (FREE $25 Credit) ⭐⭐⭐⭐

**Why:** $25 free credit, Llama 3.1 405B available

**Steps:**
1. Go to https://api.together.xyz/
2. Sign up
3. Go to Settings → API Keys
4. Create new API key
5. Copy the key
6. Add to `.env`:
   ```
   TOGETHER_API_KEY=your_key_here
   ```

---

### 3. OpenRouter (Current Setup)

**Already configured!** Your current key is in `.env`

**To get more credits:**
1. Go to https://openrouter.ai/
2. Sign in
3. Go to Settings → Credits
4. Add credits ($5 minimum)

---

### 4. Google Gemini (Current Setup)

**Already configured!** Your current key is in `.env`

**To get new key:**
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with Google
3. Click "Create API Key"
4. Copy key (starts with `AIzaSy...`)

---

## File Structure

```
insightx-app/
├── backend/
│   ├── .env                 # ✅ Your API keys (KEEP SECRET)
│   ├── .env.example         # Template for others
│   ├── app_simple.py        # ✅ Updated to use .env
│   └── requirements.txt     # ✅ Includes python-dotenv
└── .gitignore              # ✅ Excludes .env from git
```

---

## Security Best Practices

### ✅ DO:
- Keep `.env` file secret
- Never commit `.env` to git
- Use `.env.example` as template
- Rotate keys regularly
- Use different keys for dev/prod

### ❌ DON'T:
- Share `.env` file
- Commit API keys to git
- Hardcode keys in code
- Use production keys in dev
- Share keys in screenshots

---

## Environment Variables Reference

### API Keys
```bash
# Required
OPENROUTER_API_KEY=sk-or-v1-...    # DeepSeek models
GEMINI_API_KEY=AIzaSy...           # Google Gemini

# Optional (Recommended)
GROQ_API_KEY=gsk_...               # Groq (500K free/day)
TOGETHER_API_KEY=...               # Together AI ($25 credit)
```

### Database
```bash
DATABASE_PATH=data/chat_history.db  # SQLite database location
```

### Server
```bash
FLASK_DEBUG=True                    # Enable debug mode
FLASK_PORT=5000                     # Server port
FLASK_HOST=127.0.0.1               # Server host
```

---

## Testing Your Setup

### 1. Check if .env is loaded
```bash
cd insightx-app/backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenRouter:', os.getenv('OPENROUTER_API_KEY')[:20] + '...')"
```

### 2. Start backend
```bash
python app_simple.py
```

You should see:
```
[OK] Multi-LLM service initialized
[OK] Chat database initialized
==================================================
InsightX Backend Server
Running on http://127.0.0.1:5000
==================================================
```

### 3. Test API
Open browser and go to:
```
http://localhost:5000/health
```

Should return:
```json
{
  "status": "ok",
  "message": "Backend is running",
  "dataset_loaded": true,
  "rows": 250000
}
```

---

## Troubleshooting

### Error: "OPENROUTER_API_KEY not set"

**Solution:**
1. Check `.env` file exists in `backend/` folder
2. Check key is not empty or placeholder
3. Restart backend server

### Error: "No module named 'dotenv'"

**Solution:**
```bash
pip install python-dotenv
```

### Error: "API key invalid"

**Solution:**
1. Check key is correct (no extra spaces)
2. Check key hasn't expired
3. Get new key from provider

### Keys not loading

**Solution:**
1. Ensure `.env` is in `backend/` folder (same as `app_simple.py`)
2. Check file is named exactly `.env` (not `.env.txt`)
3. Restart Python/backend

---

## Sharing Your Project

### For Git/GitHub:

1. **Never commit `.env`** - It's already in `.gitignore`

2. **Share `.env.example`** instead:
   ```bash
   cp backend/.env backend/.env.example
   # Edit .env.example and replace real keys with placeholders
   ```

3. **In README, tell users:**
   ```markdown
   ## Setup
   1. Copy `.env.example` to `.env`
   2. Add your API keys to `.env`
   3. Run `python app_simple.py`
   ```

### For Team Members:

1. Share `.env.example` file
2. Tell them to:
   - Copy to `.env`
   - Get their own API keys
   - Fill in the keys

---

## Adding New API Keys

### Example: Adding Anthropic Claude

1. **Get API key** from https://console.anthropic.com/

2. **Add to `.env`:**
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Update code:**
   ```python
   # backend/app_simple.py
   ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
   ```

4. **Update `.env.example`:**
   ```bash
   ANTHROPIC_API_KEY=your-anthropic-key-here
   ```

---

## Current Configuration

Your `.env` file currently has:

✅ **OpenRouter API Key** - Configured
✅ **Gemini API Key** - Configured
⚠️ **Groq API Key** - Not configured (add for free 500K tokens/day)
⚠️ **Together API Key** - Not configured (add for $25 free credit)

### Recommended Next Steps:

1. **Get Groq API key** (5 minutes, free)
   - Go to https://console.groq.com/
   - Sign up
   - Get API key
   - Add to `.env`

2. **Get Together AI key** (5 minutes, $25 free)
   - Go to https://api.together.xyz/
   - Sign up
   - Get API key
   - Add to `.env`

3. **Test everything:**
   ```bash
   python app_simple.py
   ```

---

## Summary

✅ `.env` file created with your current keys
✅ `.env.example` created as template
✅ `.gitignore` updated to exclude `.env`
✅ `app_simple.py` updated to use environment variables
✅ `python-dotenv` added to requirements

**Your API keys are now secure and not hardcoded!**

For questions or issues, check the troubleshooting section above.
