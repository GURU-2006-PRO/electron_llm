# InsightX Analytics 🚀

> **AI-Powered Conversational Analytics for Payment Transaction Data**

InsightX is a production-ready desktop application that transforms complex payment transaction data into actionable insights using advanced AI. Ask questions in natural language, get instant answers with interactive visualizations.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Electron](https://img.shields.io/badge/electron-28.0-blue.svg)

---

## 📥 Download & Installation

### Windows Users

**[📦 Download InsightX Analytics (Google Drive)](https://drive.google.com/drive/folders/1wpFPZZvD3nB388t-_6lFiXEOjmyfkmxK?usp=sharing)**

### Installation Steps

1. **Download the EXE**
   - Click the Google Drive link above
   - Download `InsightX Analytics Setup 1.0.0.exe` (or portable version)

2. **Install the Application**
   - Run the downloaded EXE file
   - Follow the installation wizard
   - Launch from Start Menu or Desktop shortcut

3. **Get Free API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key (starts with `AIzaSy...`)

4. **Configure the App**
   - Open InsightX Analytics
   - Click "API Keys" button (top right)
   - Paste your Gemini API key
   - Click "Save"

5. **Restart & Start Analyzing**
   - Close the app completely
   - Open it again
   - Wait for "Connected" status (green dot)
   - Start asking questions!

**Why restart?** The backend loads API keys only once at startup. Restarting makes it read your newly saved keys.

---

## 🔧 Detailed Setup Guide

### Step 1: Installation
1. Download `InsightX Analytics Setup 1.0.0.exe` from [Releases](https://github.com/GURU-2006-PRO/electron_llm/releases/latest)
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### Step 2: Get Free API Keys

**Why API keys are needed:**
InsightX uses Google's Gemini AI to analyze your data. API keys connect the app to Google's AI service. They're completely free with generous quotas!

**Get your key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy...`)

### Step 3: Configure the App
1. Open InsightX Analytics
2. Click "API Keys" button (top right corner)
3. Paste your Gemini API key in the first field
4. Click "Save" button
5. You'll see a success message

### Step 4: Restart Required

**Why restart?**
The backend AI engine loads API keys only once when it starts. Restarting makes it read your newly saved configuration file.

**How to restart:**
1. Close the app completely (click X)
2. Wait 2 seconds
3. Open InsightX Analytics again
4. Wait for "Connected" status (green dot at bottom)

### Step 5: Start Analyzing!

Try these queries:
```
How many transactions are there?
Which banks have the highest failure rates?
Show me top 10 states by transaction volume
Compare Android vs iOS transaction success
What are the peak hours for transactions?
Find anomalies in high-value weekend transactions
```

---

## ✨ Key Features

### 🤖 Multi-Model AI Intelligence
- **3 Gemini Models**: Gemini 3.0 Flash Preview + 2x Gemini 2.5 Flash with automatic fallback
- **Smart Model Selection**: Choose your preferred model or let the system decide
- **Quota Management**: Seamless switching when limits are reached
- **Advanced Reasoning**: 7-step analysis chain for deep insights

### 📊 Interactive Visualizations
- **6 Chart Types**: Vertical Bar, Horizontal Bar, Line, Area, Pie, Donut
- **User-Driven Design**: AI generates data, you choose how to visualize it
- **Apache ECharts**: Professional, interactive charts with tooltips and zoom
- **Export Options**: Download charts as PNG or data as CSV
- **Fullscreen Mode**: Detailed chart exploration

### 💬 Natural Language Queries
- **Ask Anything**: "Which bank has the highest failure rate?"
- **Auto-Suggestions**: Real-time query completion
- **Chat History**: 50-query history with search
- **Context Awareness**: Follow-up questions understand previous context

### 📈 Advanced Analytics
- **Statistical Analysis**: Hypothesis testing, correlation analysis
- **Anomaly Detection**: Automatic identification of unusual patterns
- **Trend Analysis**: Time-based pattern recognition
- **Business Insights**: Actionable recommendations with confidence scores

### 🎨 Modern Desktop Experience
- **Electron App**: Native performance, works offline
- **Dark Theme**: Professional, eye-friendly interface
- **Responsive Design**: Adapts to any window size
- **Fast Performance**: Handles 250K+ rows efficiently

---

## 🚀 Quick Start

### For End Users (Windows)

**Download & Install:**
1. Download `InsightX Analytics Setup.exe` from releases
2. Run the installer
3. Launch InsightX Analytics from Start Menu

**First Time Setup:**
1. Click "API Keys" button in the app
2. Get free API keys from [Google AI Studio](https://aistudio.google.com/app/apikey)
3. Paste your keys and click Save
4. Restart the app
5. Start asking questions!

**Sample Questions:**
```
"Show me top 10 states by transaction volume"
"Which banks have the highest failure rates?"
"Compare Android vs iOS transaction success"
"What are the peak hours for transactions?"
```

---

## 💻 For Developers

### Prerequisites
- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.13+ ([Download](https://python.org))
- **Git** ([Download](https://git-scm.com))

### Installation

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/insightx-app.git
cd insightx-app
```

**2. Install Dependencies**
```bash
# Frontend dependencies
npm install

# Backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

**3. Configure API Keys**

Copy `.env.example` to `.env` in the `backend` folder:
```bash
cd backend
copy .env.example .env
```

Edit `backend/.env` with your API keys:
```env
# Get free keys from https://aistudio.google.com/app/apikey
GEMINI_API_KEY_3_FLASH=your-gemini-3-flash-key
GEMINI_API_KEY_2_5_FLASH_1=your-gemini-2.5-flash-key-1
GEMINI_API_KEY_2_5_FLASH_2=your-gemini-2.5-flash-key-2
```

**4. Run Development Mode**
```bash
npm start
```

The app will open automatically with the backend running.

---

## 🏗️ Building the EXE

### Build Complete Application

```bash
rebuild-clean.bat
```

This will:
1. Clean all old builds
2. Build Python backend into standalone EXE
3. Build Electron frontend
4. Package everything together
5. Create installer in `release/` folder

**Output:**
- `release/InsightX Analytics Setup 1.0.0.exe` - Installer
- `release/win-unpacked/InsightX Analytics.exe` - Portable version

### Build Steps Explained

**Backend Build:**
```bash
cd backend
pyinstaller build_backend.spec --clean
```

**Frontend Build:**
```bash
npm run build
```

---

## 📁 Project Structure

```
insightx-app/
├── backend/                          # Python Flask Backend
│   ├── api_server.py                # Main Flask server (all endpoints)
│   ├── gemini_config.py             # Multi-model AI configuration
│   ├── llm_client.py                # LLM service orchestration
│   ├── prompt_engine.py             # Advanced prompt templates
│   ├── database.py                  # SQLite chat history
│   ├── statistical_analysis.py      # Statistical tests
│   ├── anomaly_detector.py          # Anomaly detection
│   ├── chart_generator.py           # Chart data formatting
│   ├── feature_manager.py           # Feature flags
│   ├── model_service.py             # Model management
│   ├── method_explainer.py          # Statistical method explanations
│   ├── proactive_insights.py        # Automatic insights
│   ├── query_suggestions.py         # Query autocomplete
│   ├── statistical_significance.py  # Significance testing
│   ├── build_backend.spec           # PyInstaller configuration
│   ├── .env                         # API keys (not in git)
│   ├── .env.example                 # API key template
│   ├── requirements.txt             # Python dependencies
│   └── data/
│       ├── upi_transactions_2024.csv  # Dataset (250K rows)
│       └── chat_history.db          # SQLite database
├── features/                        # Frontend Features
│   ├── enhancements.js              # UI enhancements
│   ├── icon-actions.js              # Export & report generation
│   └── india-map-data.json          # Geographic data
├── styles/                          # CSS Styling
│   └── cursor-style.css             # Main stylesheet
├── assets/                          # Application Assets
│   └── logo.png                     # App icon
├── index_simple.html                # Main UI
├── renderer_simple.js               # Frontend logic
├── main.js                          # Electron main process
├── chart-enhancements.js            # Apache ECharts integration
├── chart-system.js                  # Chart rendering system
├── rebuild-clean.bat                # Complete build script
├── package.json                     # Node dependencies & build config
├── README.md                        # This file
├── TECHNICAL-DOCUMENTATION.md       # System architecture
├── 20-DIVERSE-QUERIES-EXPLAINED.txt # Sample queries
└── FIX-EXE-ISSUES.md               # Troubleshooting guide
```

---

## 🎯 How It Works

### 1. User Asks Question
```
"Which bank has the highest failure rate?"
```

### 2. AI Processes Query
- Classifies query complexity
- Selects appropriate model
- Generates Pandas code
- Executes analysis
- Formats results

### 3. Results Displayed
- Data table with key metrics
- Insights and recommendations
- Chart type selector (6 options)
- Interactive visualization

### 4. User Actions
- Export data as CSV
- Download chart as PNG
- Generate HTML report
- Ask follow-up questions

---

## 🔧 Configuration

### API Keys

The app supports multiple Gemini API keys for high availability:

| Key | Model | Quota | Purpose |
|-----|-------|-------|---------|
| `GEMINI_API_KEY_3_FLASH` | Gemini 3.0 Flash Preview | 20/day | Latest features |
| `GEMINI_API_KEY_2_5_FLASH_1` | Gemini 2.5 Flash | 1500/day | Primary fallback |
| `GEMINI_API_KEY_2_5_FLASH_2` | Gemini 2.5 Flash | 1500/day | Secondary fallback |

**Get Free Keys:** https://aistudio.google.com/app/apikey

### Dataset

The app includes a sample dataset of 250,000 UPI transactions with:
- **17 columns**: transaction details, merchant info, device data, fraud flags
- **Real patterns**: failures, fraud, network issues
- **Indian context**: States, banks, merchant categories

**Location:** `backend/data/upi_transactions_2024.csv`

---

## 📊 Technical Stack

### Frontend
- **Electron 28.0** - Desktop application framework
- **Apache ECharts 5.4** - Interactive visualizations
- **Vanilla JavaScript** - No framework overhead
- **Custom CSS** - Modern dark theme

### Backend
- **Python 3.13** - Core language
- **Flask 3.0** - RESTful API server
- **Pandas 2.1** - Data processing
- **Google Generative AI** - Multi-model integration
- **SQLite** - Chat history persistence

### Build Tools
- **PyInstaller** - Python to EXE
- **electron-builder** - Electron packaging
- **NSIS** - Windows installer

---

## 🎨 Features in Detail

### Multi-Model AI System
```python
# Automatic fallback on quota errors
models = [
    ("gemini-3-flash", key1, 20),
    ("gemini-2.5-flash-1", key2, 1500),
    ("gemini-2.5-flash-2", key3, 1500)
]

for model, key, quota in models:
    try:
        return call_model(model, key, prompt)
    except QuotaExceeded:
        continue  # Try next model
```

### 7-Step Reasoning Chain
1. **Volume Validation**: Calculate segment percentages
2. **Domain Reasoning**: Apply payment system knowledge
3. **Correlation Analysis**: Identify relationships
4. **Pattern Recognition**: Detect compound patterns
5. **Root Cause**: Explain WHY patterns exist
6. **Business Impact**: Quantify cost of inaction
7. **Recommendations**: Provide specific solutions

### Chart System
- **Data-First Approach**: AI generates optimal data structure
- **User Choice**: Pick visualization that makes sense to you
- **Interactive**: Hover tooltips, zoom, pan
- **Export**: PNG download with transparent background

---

## 🐛 Troubleshooting

### App Won't Start
- Check if port 5000 is available
- Verify Python 3.13+ is installed
- Check backend logs in console (Ctrl+Shift+I)

### Backend Not Connecting
- Ensure `api_server.exe` is in `resources/backend/dist/`
- Check `.env` file exists in `resources/backend/`
- Verify data folder has CSV file

### API Key Errors
- Get free keys from https://aistudio.google.com/app/apikey
- Update keys in app (API Keys button)
- Restart app after updating keys

### Charts Not Rendering
- Try different chart type
- Check data has valid numbers
- Clear cache and restart

See `FIX-EXE-ISSUES.md` for detailed troubleshooting.

---

## 📈 Performance

- **Query Response**: 2-5 seconds
- **Dataset Size**: Handles 250K+ rows
- **Memory Usage**: ~350MB total
- **Chart Rendering**: <500ms
- **Export Speed**: <3 seconds

---

## 🚀 Future Roadmap

- [ ] User dataset upload (drag & drop CSV)
- [ ] Custom column mapping
- [ ] Predictive analytics (fraud prediction)
- [ ] Real-time data streaming
- [ ] Multi-user collaboration
- [ ] Advanced visualizations (heatmaps, sankey)
- [ ] Mobile app version

---

## 📚 Documentation

- **README.md** - This file (getting started)
- **TECHNICAL-DOCUMENTATION.md** - Complete system architecture
- **20-DIVERSE-QUERIES-EXPLAINED.txt** - Sample queries with explanations
- **FIX-EXE-ISSUES.md** - Troubleshooting guide

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **Google Gemini** - Multi-model AI platform
- **Apache ECharts** - Professional visualizations
- **Electron** - Desktop app framework
- **Flask** - Python web framework
- **Pandas** - Data processing library

---

## 📧 Support

- **Issues**: Open a GitHub issue
- **Email**: [your-email@example.com]
- **Documentation**: See docs folder

---

**Built with ❤️ for data-driven decision making**
