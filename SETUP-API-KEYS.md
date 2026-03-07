# Setup API Keys - Quick Guide

## For Users Who Downloaded the EXE

### Step 1: Get Your API Keys
1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **"Create API Key"** button
4. Create **3 different API keys** (for redundancy)
5. Copy each key immediately (they look like: `AIzaSy...`)

### Step 2: Add Keys to InsightX
1. Open **InsightX Analytics** app
2. Click the **Settings** icon (⚙️) in the top right corner
3. Paste your 3 API keys:
   - **Gemini 3.0 Flash (Primary)** - Paste first key
   - **Gemini 2.5 Flash #1 (Fallback)** - Paste second key
   - **Gemini 2.5 Flash #2 (Backup)** - Paste third key
4. Click **"Save API Keys"** button
5. **Close and restart** the app

### Step 3: Test It
1. Type a simple query: `"tell me the total rows"`
2. If it works → ✅ You're all set!
3. If you see an error → Check the error message for specific issue

---

## For Developers (Running from Source)

### Step 1: Copy the Example File
```bash
cd insightx-app/backend
cp .env.example .env
```

### Step 2: Get Your API Keys
1. Go to https://aistudio.google.com/app/apikey
2. Create 3 different API keys
3. Copy each key

### Step 3: Edit .env File
Open `backend/.env` and replace the placeholder values:

```env
GEMINI_API_KEY_3_FLASH=AIzaSy...your-actual-key-1
GEMINI_API_KEY_2_5_FLASH_1=AIzaSy...your-actual-key-2
GEMINI_API_KEY_2_5_FLASH_2=AIzaSy...your-actual-key-3
```

### Step 4: Start the App
```bash
npm start
```

---

## Important Security Notes

⚠️ **NEVER share your API keys** - They are like passwords

⚠️ **NEVER commit .env to git** - Already in .gitignore

⚠️ **NEVER share screenshots with keys visible** - Google auto-detects and blocks them

⚠️ **Each user needs their own keys** - Don't share keys between users

---

## Troubleshooting

### "API key was reported as leaked"
- Your key was exposed (screenshot, GitHub, etc.)
- Go to https://aistudio.google.com/app/apikey
- **Delete the leaked key**
- Create a NEW key
- Update it in Settings

### "API request timed out"
- Check your internet connection
- Try again in a few seconds
- If it persists, the Gemini API might be down

### "API quota exceeded"
- You've used all 20 requests for today (Gemini 3.0)
- Wait until tomorrow, or
- Use a different API key

---

## Why 3 Keys?

- **Gemini 3.0 Flash**: 20 requests/day (newest model)
- **Gemini 2.5 Flash #1**: 1500 requests/day (fallback)
- **Gemini 2.5 Flash #2**: 1500 requests/day (backup)

The app automatically switches between keys if one runs out of quota.
