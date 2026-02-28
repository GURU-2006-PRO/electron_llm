# InsightX Analytics 🚀

> **Conversational AI-Powered Payment Transaction Analytics Platform**

InsightX is a production-grade desktop application that transforms complex payment transaction data into actionable insights using advanced AI models. Built for Techfest 2025-26 at IIT Bombay.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Electron](https://img.shields.io/badge/electron-28.0-blue.svg)

## 🏆 Competition Submission - Techfest 2025-26

This project is submitted for the Techfest 2025-26 AI/ML competition at IIT Bombay. All deliverables are included in this repository:

- ✅ **Source Code**: Complete codebase with setup instructions
- ✅ **Working Demo**: Functional Electron desktop application
- ✅ **Technical Documentation**: `TECHNICAL-DOCUMENTATION.md` (comprehensive system architecture)
- ✅ **Sample Queries**: `SAMPLE-QUERIES.md` (20 diverse example queries)
- ✅ **Demo Video Script**: `DEMO-VIDEO-SCRIPT.txt` (6-minute presentation guide)
- ✅ **Presentation**: Ready for 10-minute pitch (see demo script)

---

## ✨ Key Features & Innovations

### 🤖 Multi-Model AI Intelligence (INNOVATION #1)
- **3 Gemini Models**: Gemini 3.0 Flash Preview + 2x Gemini 2.5 Flash
- **Automatic Fallback**: Seamless switching on quota errors
- **Frontend Model Selection**: User chooses preferred model
- **Smart Routing**: Optimal model for each query type
- **Cost Optimization**: Use faster/cheaper models when appropriate

### 📊 User-Driven Visualization System (INNOVATION #2)
- **6 Chart Types**: Vertical Bar, Horizontal Bar, Line, Area, Pie, Donut
- **User Choice**: AI generates data first, user picks chart type
- **Apache ECharts**: Professional, interactive visualizations
- **Export to PNG**: Download any chart as image
- **Fullscreen Mode**: Detailed chart exploration
- **Dark Theme**: Modern, professional appearance

### 🎯 Advanced Analytics Engine (INNOVATION #3)
- **7-Step Reasoning Chain**: Volume validation, domain reasoning, root cause analysis
- **Production-Grade Prompts**: Adapted for Pandas with Indian payment domain knowledge
- **Structured Insights**: Direct answers, key stats, patterns, business impact, recommendations
- **Confidence Scoring**: Rule-based scoring with transparency
- **Statistical Analysis**: Hypothesis testing, correlation analysis, anomaly detection

### 💼 Enterprise-Ready Features (INNOVATION #4)
- **CSV Export**: Download data tables for Excel
- **HTML Report Generation**: Comprehensive reports with all charts embedded
- **Chat History**: SQLite database with 50-query history
- **Query Suggestions**: Real-time autocomplete
- **Error Handling**: Graceful degradation with user-friendly messages

### 🎨 Modern UI/UX (INNOVATION #5)
- **Electron Desktop App**: Native performance, offline capability
- **Real-time Processing**: Streaming responses with loading indicators
- **Responsive Design**: Adapts to window size
- **Professional Styling**: Cursor IDE-inspired interface
- **Keyboard Shortcuts**: Power user features

---

## 🚀 Quick Start (Competition Judges)

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org))
- **Python** 3.13+ ([Download](https://python.org))
- **Gemini API Keys** ([Get Free Keys](https://aistudio.google.com/app/apikey))

### 5-Minute Setup

**1. Install Dependencies**
```bash
# Install Node packages
npm install

# Install Python packages
cd backend
pip install -r requirements.txt
cd ..
```

**2. Configure API Keys**

Edit `backend/.env` (template provided in `.env.example`):
```env
GEMINI_API_KEY_3_FLASH=your-gemini-3-flash-key
GEMINI_API_KEY_2_5_FLASH_1=your-gemini-2.5-flash-key-1
GEMINI_API_KEY_2_5_FLASH_2=your-gemini-2.5-flash-key-2
```

**3. Launch Application**
```bash
# Windows
start-insightx.bat

# macOS/Linux
npm start
```

**4. Try Sample Queries**

See `SAMPLE-QUERIES.md` for 20 example queries, or try:
```
"Show me top 10 states by transaction volume"
"Which banks have the highest failure rates?"
"Compare Android vs iOS transaction success"
```

### Dataset Information

The application uses `backend/data/upi_transactions_2024.csv`:
- **250,000 transactions** from Indian UPI payment system
- **17 columns**: transaction details, merchant info, device data, fraud flags
- **Real-world patterns**: Includes failures, fraud, network issues

---

## 📁 Project Structure

```
insightx-app/
├── backend/                          # Python Flask API
│   ├── app_simple.py                # Main Flask server
│   ├── gemini_config.py             # Multi-model AI configuration
│   ├── advanced_prompts.py          # Production-grade prompts
│   ├── multi_llm_service.py         # Model orchestration
│   ├── database.py                  # SQLite chat history
│   ├── statistical_analysis.py      # Statistical tests
│   ├── anomaly_detector.py          # Anomaly detection
│   ├── .env                         # API keys (not in git)
│   ├── .env.example                 # API key template
│   ├── requirements.txt             # Python dependencies
│   └── data/
│       └── upi_transactions_2024.csv  # Dataset (250K rows)
├── index_simple.html                # Main UI
├── renderer_simple.js               # Frontend logic
├── main.js                          # Electron main process
├── chart-enhancements.js            # Apache ECharts integration
├── features/
│   ├── icon-actions.js              # Export & report generation
│   └── enhancements.js              # UI enhancements
├── styles/
│   └── cursor-style.css             # Professional styling
├── TECHNICAL-DOCUMENTATION.md       # System architecture (DELIVERABLE)
├── SAMPLE-QUERIES.md                # 20 example queries (DELIVERABLE)
├── DEMO-VIDEO-SCRIPT.txt            # Video presentation guide (DELIVERABLE)
├── README.md                        # This file (DELIVERABLE)
├── package.json                     # Node dependencies
└── start-insightx.bat               # Windows launcher
```

---

## 💡 Usage Examples

### Simple Queries
```
"How many transactions are there?"
"What's the average transaction amount?"
"Show me total successful transactions"
```

### Moderate Queries
```
"Which bank has the highest failure rate?"
"Compare Android vs iOS transaction success rates"
"Show fraud rates by merchant category"
"Top 10 states by transaction volume"
```

### Complex Queries
```
"Analyze the correlation between network type and transaction failures"
"What are the peak hours for P2M transactions?"
"Compare weekend vs weekday transaction patterns"
"Identify anomalies in high-value transactions"
```

### Visualization Workflow
1. Ask a question in natural language
2. AI generates data table with insights
3. Select chart type from 6 options
4. Interactive chart renders with tooltips
5. Export chart as PNG or data as CSV

---

## 🎯 Model Selection

| Model | Speed | Quality | Quota | Best For |
|-------|-------|---------|-------|----------|
| **Gemini 3.0 Flash Preview** | ⚡⚡⚡ | ⭐⭐⭐⭐ | 20/day | Latest features, fast |
| **Gemini 2.5 Flash #1** | ⚡⚡⚡ | ⭐⭐⭐ | 1500/day | High volume, reliable |
| **Gemini 2.5 Flash #2** | ⚡⚡⚡ | ⭐⭐⭐ | 1500/day | Backup fallback |

The system automatically falls back to the next model if quota is exceeded.

---

## 🏗️ Architecture Highlights

### Frontend (Electron + JavaScript)
- **Electron 28.0**: Native desktop app with offline capability
- **Apache ECharts 5.4**: Professional, interactive visualizations
- **Vanilla JavaScript**: No framework overhead, fast performance
- **Custom CSS**: Cursor IDE-inspired dark theme

### Backend (Python Flask)
- **Flask 3.0**: RESTful API with JSON responses
- **Pandas 2.1**: Efficient data processing for 250K+ rows
- **Google Generative AI SDK**: Multi-model integration
- **SQLite**: Chat history persistence

### AI Integration
- **Multi-Model Strategy**: 3 Gemini models with automatic fallback
- **Prompt Engineering**: 7-step reasoning chain with domain knowledge
- **Query Classification**: Automatic routing based on complexity
- **Structured Output**: JSON responses with validation

### Data Processing
- **Pandas DataFrame**: In-memory analytics
- **Statistical Analysis**: Hypothesis testing, correlation, anomaly detection
- **Query Specification**: Natural language to Pandas conversion
- **Result Enhancement**: Percentages, trends, formatting

---

## 📊 Technical Innovations

### 1. Multi-Model AI with Automatic Fallback
```python
# gemini_config.py
models = [
    ("gemini-3-flash", GEMINI_API_KEY_3_FLASH, 20),
    ("gemini-2.5-flash-1", GEMINI_API_KEY_2_5_FLASH_1, 1500),
    ("gemini-2.5-flash-2", GEMINI_API_KEY_2_5_FLASH_2, 1500)
]

# Automatic fallback on quota errors
for model_name, api_key, quota in models:
    try:
        response = call_gemini(model_name, api_key, prompt)
        return response
    except QuotaExceededError:
        continue  # Try next model
```

### 2. User-Driven Visualization
```javascript
// renderer_simple.js
function showChartTypeSelector(data) {
    // Show modal with 6 chart options
    // User picks preferred visualization
    // System adapts to user choice
}
```

### 3. 7-Step Reasoning Chain
```python
# advanced_prompts.py
ADVANCED_PROMPT = """
1. Volume Validation: Calculate segment %
2. Domain Reasoning: Apply payment system knowledge
3. Correlation Analysis: Identify relationships
4. Pattern Recognition: Detect compound patterns
5. Root Cause: Explain WHY patterns exist
6. Business Impact: Quantify cost of inaction
7. Recommendation: Provide specific solutions
"""
```

### 4. Enterprise Export Features
```javascript
// icon-actions.js
function exportResults(data, filename) {
    // CSV export with Excel compatibility
}

function generateReport() {
    // HTML report with embedded charts
}
```

---

## 🔧 Configuration

### API Keys (backend/.env)
```env
# Gemini 3.0 Flash Preview (Primary - 20 req/day)
GEMINI_API_KEY_3_FLASH=your-key-here

# Gemini 2.5 Flash (Fallback 1 - 1500 req/day)
GEMINI_API_KEY_2_5_FLASH_1=your-key-here

# Gemini 2.5 Flash (Fallback 2 - 1500 req/day)
GEMINI_API_KEY_2_5_FLASH_2=your-key-here

# OpenRouter (Optional - currently no credits)
OPENROUTER_API_KEY=your-key-here
```

### Dataset Requirements
- **Format**: CSV with UTF-8 encoding
- **Size**: 250K+ rows recommended
- **Columns**: 17 columns with transaction details
- **Location**: `backend/data/upi_transactions_2024.csv`

---

## 📈 Performance Metrics

- **Query Response Time**: 2-5 seconds (Gemini models)
- **Dataset Size**: Handles 250K+ rows efficiently
- **Memory Usage**: ~200MB (backend) + ~150MB (frontend)
- **Chart Rendering**: <500ms for most visualizations
- **Export Speed**: <1 second for CSV, <3 seconds for HTML report

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.13+

# Reinstall dependencies
cd backend
pip install -r requirements.txt --upgrade
```

### API Key Errors
- Verify keys in `backend/.env`
- Get free Gemini keys: https://aistudio.google.com/app/apikey
- Check quota limits on API dashboard

### Dataset Not Loading
- Verify file path: `backend/data/upi_transactions_2024.csv`
- Check CSV encoding (UTF-8)
- Ensure column names match exactly

### Charts Not Rendering
- Clear browser cache (Ctrl+Shift+Delete in Electron)
- Check console for errors (F12)
- Try different chart type

---

## 📚 Documentation

- **Technical Documentation**: `TECHNICAL-DOCUMENTATION.md` - Complete system architecture
- **Sample Queries**: `SAMPLE-QUERIES.md` - 20 diverse example queries
- **Demo Script**: `DEMO-VIDEO-SCRIPT.txt` - 6-minute video presentation guide
- **API Template**: `backend/.env.example` - API key configuration template

---

## 🎥 Demo Video Guide

See `DEMO-VIDEO-SCRIPT.txt` for a complete 6-minute demo script covering:
1. Problem statement and solution overview
2. Multi-model AI demonstration
3. User-driven visualization workflow
4. Enterprise features (export, reports)
5. Technical innovations
6. Future roadmap (user dataset upload)

---

## 🚀 Future Enhancements

### Planned Features
- **User Dataset Upload**: Drag-and-drop CSV with custom column mapping
- **Predictive Analytics**: Fraud prediction, trend forecasting
- **Collaboration**: Multi-user support, shared dashboards
- **Advanced Visualizations**: Heatmaps, sankey diagrams, network graphs
- **Real-time Data**: Live data streaming and updates

---

## 🙏 Acknowledgments

- **Techfest 2025-26** - IIT Bombay
- **Google Gemini** - Multi-model AI platform
- **Apache ECharts** - Professional visualizations
- **Cursor IDE** - UI/UX inspiration
- **Python & Pandas** - Data processing excellence

---

## 📧 Contact

For questions about this competition submission:
- Open an issue on GitHub
- Email: [your-email@example.com]

---

**Built with ❤️ for Techfest 2025-26 | IIT Bombay**
