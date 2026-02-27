# InsightX Analytics 🚀

> **Conversational AI-Powered Payment Transaction Analytics Platform**

InsightX is a production-grade desktop application that transforms complex payment transaction data into actionable insights using advanced AI models. Built for Techfest 2025-26 at IIT Bombay.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Electron](https://img.shields.io/badge/electron-28.0-blue.svg)

---

## ✨ Key Features

### 🤖 Multi-Model AI Intelligence
- **DeepSeek R1**: Advanced reasoning for complex decomposition analysis
- **DeepSeek Chat**: Balanced speed and quality for moderate queries
- **Gemini 2.5 Flash**: Lightning-fast responses for simple queries
- **Auto-Classification**: Intelligent query routing based on complexity

### 📊 Interactive Visualizations
- Apache ECharts integration with 5 chart types
- Horizontal/Vertical bar charts with gradient colors
- Line charts with smooth curves
- Area charts for cumulative trends
- Donut/Pie charts for distribution analysis
- Dark theme with responsive design

### 🎯 Advanced Analytics Engine
- **7-Step Reasoning Chain**: Volume validation, domain reasoning, root cause analysis
- **Production-Grade Prompts**: Adapted for Pandas with Indian payment domain knowledge
- **Structured Insights**: Direct answers, key stats, patterns, business impact, recommendations
- **Confidence Scoring**: Rule-based scoring with transparency
- **Follow-up Questions**: Intelligent suggestions for deeper analysis

### 🎨 Modern UI/UX
- Cursor IDE-style resizable sidebars (drag-to-resize)
- Real-time query processing with streaming responses
- Advanced Mode toggle for 10/10 quality insights
- Model selection with auto-classification badge
- Export capabilities (CSV, JSON, Excel)

### 📈 Advanced Analytics Dashboard
- **6 KPI Cards** with real-time metrics and trend indicators:
  - Total Transactions (↑↓ vs yesterday)
  - Success Rate (%)
  - Failure Rate (%)
  - Fraud Flag Rate (%)
  - Average Transaction Amount (₹)
  - Total Transaction Volume (₹)
- **4 Overview Charts** auto-loaded on startup:
  - Transaction Volume Trend (7-day line chart)
  - Top Banks by Volume (horizontal bar chart)
  - Transaction Type Distribution (donut chart)
  - Hourly Transaction Pattern (bar chart)
- **Interactive Drill-Down**: Click any KPI or chart element to auto-generate insights
- **Export Dashboard**: Download all charts as PNG images
- **Refresh on Demand**: Update dashboard data with one click

### 🔍 Query History & Bookmarks
- Stores last 50 queries in localStorage
- Bookmark favorite queries with star icon
- Quick access via history button or `Ctrl+H`
- Time ago display (e.g., "2h ago", "Just now")
- Click any history item to reuse query

---

## 🏗️ Architecture

```
insightx-app/
├── backend/                    # Python Flask API
│   ├── app_simple.py          # Main Flask server
│   ├── advanced_prompts.py    # Production-grade prompt engineering
│   ├── multi_llm_service.py   # Multi-model orchestration
│   ├── ml_models.py           # ML utilities
│   ├── llm_service.py         # LLM client wrapper
│   └── data/                  # Dataset storage
│       └── upi_transactions_2024.csv
├── index_simple.html          # Main UI
├── renderer_simple.js         # Frontend logic
├── main.js                    # Electron main process
├── llm-handler.js            # LLM communication
├── styles/                    # CSS styling
│   └── cursor-style.css
└── features/                  # Feature modules
    └── icon-actions.js
```

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.13+
- **OpenRouter API Key** (for DeepSeek models)
- **Google Gemini API Key** (for Gemini Flash)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd insightx-app
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
cd ..
```

4. **Configure API Keys**

Edit `backend/app_simple.py` and update:
```python
OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
GEMINI_API_KEY = "your-gemini-key-here"
```

5. **Add your dataset**

Place your CSV file at:
```
backend/data/upi_transactions_2024.csv
```

Expected columns:
- transaction id, timestamp, transaction type
- merchant_category, amount (INR), transaction_status
- sender_age_group, receiver_age_group, sender_state
- sender_bank, receiver_bank, device_type, network_type
- fraud_flag, hour_of_day, day_of_week, is_weekend

6. **Launch the application**
```bash
npm start
```

Or use the batch file (Windows):
```bash
start-insightx.bat
```

---

## 💡 Usage Examples

### Dashboard Interaction
When you load the application, the dashboard automatically displays:

1. **KPI Cards** (top of workspace):
   - Click any KPI card to drill down into that metric
   - Example: Click "Failure Rate" → Auto-generates "Show me failed transactions by bank"
   
2. **Overview Charts** (main workspace):
   - 4 charts load automatically with your dataset
   - Click chart elements for drill-down queries
   - Example: Click a bank name in "Top Banks" chart → "Show me detailed analysis for [Bank Name]"

3. **Dashboard Actions**:
   - **Refresh**: Update all dashboard data
   - **Export**: Download all 4 charts as PNG images

### Simple Queries (Auto → Gemini Flash)
```
"How many transactions are there?"
"What's the average transaction amount?"
"Show me total successful transactions"
```

### Moderate Queries (Auto → DeepSeek Chat)
```
"Which bank has the highest failure rate?"
"Compare Android vs iOS transaction success rates"
"Show fraud rates by merchant category"
```

### Complex Queries (Auto → DeepSeek R1)
```
"Given that weekend P2M Food transactions on 3G networks from 18-25 
age group using Android devices show 18% failure rate (vs 4.2% 
platform average), decompose this into: (a) network contribution, 
(b) merchant capacity contribution, (c) bank-side contribution, 
(d) user behavior contribution. Then recommend a prioritized 3-step 
intervention plan with expected impact percentages for each step"
```

### Advanced Mode Features
- Toggle "Advanced Mode" for production-grade insights
- Get volume validation, domain reasoning, and specific recommendations
- View reasoning chains (DeepSeek R1 explainability)
- Receive confidence scores with transparency
- Get intelligent follow-up question suggestions

---

## 🎯 Model Selection Guide

| Model | Speed | Quality | Cost | Best For |
|-------|-------|---------|------|----------|
| **Gemini 2.5 Flash** | ⚡⚡⚡ | ⭐⭐⭐ | FREE | Simple aggregations, counts |
| **DeepSeek Chat** | ⚡⚡ | ⭐⭐⭐⭐ | $ | Comparisons, trends, filters |
| **DeepSeek R1** | ⚡ | ⭐⭐⭐⭐⭐ | $$ | Decomposition, root cause, complex reasoning |
| **Auto (Smart)** | Adaptive | Optimal | Efficient | Automatic classification |

---

## 🔧 Configuration

### API Keys
Update in `backend/app_simple.py`:
```python
OPENROUTER_API_KEY = "sk-or-v1-..."
GEMINI_API_KEY = "AIzaSy..."
```

### Model Fallback Chain
Configured in `backend/multi_llm_service.py`:
1. DeepSeek R1 (primary)
2. DeepSeek Chat (fallback)
3. Gemini 2.5 Flash (final fallback)

### Query Classification
Automatic routing based on:
- **Simple**: Keywords like "count", "total", "how many"
- **Moderate**: "compare", "show", "list", "group by"
- **Complex**: "decompose", "analyze", "why", "root cause"

---

## 📊 Dataset Requirements

### Format
- CSV file with 250K+ rows recommended
- 17 columns minimum (see schema above)
- Column names can have spaces (e.g., "amount (INR)")

### Sample Data Structure
```csv
transaction id,timestamp,transaction type,merchant_category,amount (INR),...
TXN001,2024-01-01 10:30:00,P2M,Food,250.00,...
TXN002,2024-01-01 11:15:00,P2P,,1500.00,...
```

### Auto-Loading
Dataset is automatically loaded on backend startup from:
```
backend/data/upi_transactions_2024.csv
```

---

## 🎨 UI Features

### Resizable Sidebars
- Drag the edge between sidebars and workspace
- Min width: 200px, Max width: 600px
- Persists across sessions (localStorage)
- Blue highlight on hover

### Chart Interactions
- Hover tooltips with detailed data
- Responsive resize on window changes
- Smooth animations and transitions
- Dark theme matching

### Export Options
- CSV: Raw data export
- JSON: Structured data export
- Excel: Formatted spreadsheet

---

## 🔍 Advanced Prompts System

### 7-Step Reasoning Chain
1. **Strongest Signal**: Largest variance from average
2. **Correlation Direction**: Positive/Negative/None/Weak
3. **Compound Pattern Check**: Multi-column combinations
4. **Domain Explanation**: WHY patterns exist (Indian payment context)
5. **Volume Impact**: Segment % of total transactions
6. **Recommendation**: Specific technical solutions
7. **Confidence Scoring**: Rule-based transparency

### Domain Knowledge Integration
- P2P vs P2M vs Bill Payment vs Recharge
- Cross-bank transfer challenges
- 3G network packet loss patterns
- PSU vs private bank infrastructure
- Fraud flag interpretation (flagged ≠ confirmed)

### Output Structure
```json
{
  "direct_answer": "One sentence with key number",
  "key_stats": ["Stat 1", "Stat 2", "Stat 3"],
  "correlation": {
    "type": "positive|negative|none|weak",
    "description": "Exact relationship",
    "strength": "strong|moderate|weak|none"
  },
  "pattern": "Main pattern with values",
  "root_cause": "WHY this exists",
  "business_impact": {
    "segment_volume_pct": "X.X%",
    "failure_contribution_pct": "Y.Y%",
    "cost_of_inaction": "Business consequence"
  },
  "recommendation": {
    "what": "Specific problem",
    "how": "Technical solution",
    "expected_improvement": "Conservative %",
    "priority": "Quick Win|Medium Term|Strategic",
    "owner": "Engineering|Product|Operations"
  },
  "confidence": "High|Medium|Low",
  "confidence_reason": "Volume X%, variance Y%"
}
```

---

## 🛠️ Development

### Run in Development Mode
```bash
npm run dev
```

### Build for Production
```bash
# Windows
npm run build:win

# macOS
npm run build:mac

# Linux
npm run build:linux
```

### Project Structure
- **Frontend**: Electron + Vanilla JS + Apache ECharts
- **Backend**: Flask + Pandas + OpenAI SDK
- **AI Models**: OpenRouter (DeepSeek) + Google Gemini
- **Styling**: Custom CSS with Cursor IDE inspiration

---

## 📈 Performance

- **Query Response Time**: 2-8 seconds (model-dependent)
- **Dataset Size**: Handles 250K+ rows efficiently
- **Memory Usage**: ~200MB (backend) + ~150MB (frontend)
- **Concurrent Queries**: Single-threaded (Flask dev server)

### Optimization Tips
- Use Auto mode for efficient model selection
- Enable Advanced Mode only for complex queries
- Filter data before grouping for faster results
- Limit result rows to 15-20 for better visualization

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

### Dataset Not Loading
- Verify file path: `backend/data/upi_transactions_2024.csv`
- Check CSV format (UTF-8 encoding)
- Ensure column names match schema

### API Key Errors
- Verify OpenRouter key starts with `sk-or-v1-`
- Verify Gemini key starts with `AIzaSy`
- Check API quota and billing status

### JSON Parse Errors
- Update to latest `advanced_prompts.py`
- Check for Chinese/Hindi text in responses
- Verify `strip_fences()` function is working

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Techfest 2025-26** - IIT Bombay
- **DeepSeek AI** - Advanced reasoning models
- **Google Gemini** - Fast inference
- **Apache ECharts** - Beautiful visualizations
- **Cursor IDE** - UI/UX inspiration

---

## 📧 Contact

For questions, issues, or feedback:
- Open an issue on GitHub
- Email: [your-email@example.com]
- Project Link: [repository-url]

---

## 🎓 Citation

If you use InsightX in your research or project, please cite:

```bibtex
@software{insightx2025,
  title={InsightX Analytics: AI-Powered Payment Transaction Analytics},
  author={Your Name},
  year={2025},
  url={repository-url}
}
```

---

**Built with ❤️ for Techfest 2025-26 | IIT Bombay**
