# Chart Generation Workflow 📊

## Complete End-to-End Process

This document explains how charts are generated from user query to visual display.

---

## 🔄 High-Level Workflow

```
User Query → Backend Processing → Data Extraction → Chart Prompt → User Approval → Chart Generation → Display
```

---

## 📋 Detailed Step-by-Step Process

### Step 1: User Submits Query
**Location:** Frontend (`renderer_simple.js`)

```javascript
// User types query and clicks send
User: "Show me top 5 banks by transaction volume"
↓
sendQuery(query) // Called
↓
Advanced Mode: sendAdvancedQuery()
```

**What happens:**
- User types query in chat input
- Clicks send button or presses Enter
- Query sent to backend via POST request

---

### Step 2: Backend Receives Query
**Location:** Backend (`app_simple.py` → `/advanced-query` endpoint)

```python
@app.route('/advanced-query', methods=['POST'])
def advanced_query():
    user_question = data.get('query', '')
    model = data.get('model', 'auto')
```

**What happens:**
- Backend receives query
- Extracts query text and model selection
- Starts processing pipeline

---

### Step 3: Query Classification
**Location:** Backend (`advanced_prompts.py` → `PANDAS_GENERATION_PROMPT`)

```python
# STEP 1: Generate Pandas query specification
query_resp = llm_service.openrouter_client.chat.completions.create(
    model="deepseek/deepseek-chat",
    messages=[
        {"role": "system", "content": PANDAS_GENERATION_PROMPT},
        {"role": "user", "content": user_question}
    ]
)
```

**What happens:**
- LLM analyzes the query
- Determines what data is needed
- Generates query specification JSON

**Example Output:**
```json
{
  "status": "success",
  "operation": "aggregation",
  "filter_conditions": [],
  "group_by_column": "sender_bank",
  "metrics": ["count"],
  "sort_by": "count",
  "sort_order": "desc",
  "limit": 5,
  "chart_type": "horizontal_bar",
  "intent": "comparison"
}
```

**Key Field:** `chart_type` determines visualization type:
- `horizontal_bar` - Horizontal bar chart
- `vertical_bar` - Vertical bar chart
- `line` - Line chart
- `area` - Area chart
- `donut` - Donut/pie chart

---

### Step 4: Data Extraction
**Location:** Backend (`advanced_prompts.py` → `execute_pandas_query()`)

```python
# STEP 2: Execute Pandas query
result_df = execute_pandas_query(df, query_spec)
```

**What happens:**
- Pandas operations executed on dataset
- Data filtered, grouped, aggregated
- Results returned as DataFrame

**Example Result:**
```
sender_bank          count
HDFC Bank           45000
SBI                 38000
ICICI Bank          32000
Axis Bank           28000
Kotak Mahindra      25000
```

---

### Step 5: Generate Insights
**Location:** Backend (`app_simple.py` → advanced_query)

```python
# STEP 3: Generate advanced insight
insight_resp = llm_service.openrouter_client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": insight_system_prompt},
        {"role": "user", "content": f"Query Result: {result_df}"}
    ]
)
```

**What happens:**
- LLM analyzes the data results
- Generates structured insights
- Creates recommendations

**Example Insight:**
```json
{
  "direct_answer": "HDFC Bank has the highest volume with 45,000 transactions",
  "key_stats": ["HDFC: 45K", "SBI: 38K", "ICICI: 32K"],
  "pattern": "Top 3 banks account for 70% of volume",
  "recommendation": {...}
}
```

---

### Step 6: Return to Frontend
**Location:** Backend → Frontend

```python
return jsonify({
    "status": "success",
    "insight": insight,
    "data": result_df.to_dict('records'),
    "chart_type": query_spec.get("chart_type", "vertical_bar"),
    "rows_returned": len(result_df)
})
```

**What's sent:**
- ✅ Insight (text analysis)
- ✅ Data (array of objects)
- ✅ Chart type (visualization type)
- ✅ Row count

---

### Step 7: Display Insight
**Location:** Frontend (`renderer_simple.js` → `sendAdvancedQuery()`)

```javascript
if (response.data.insight) {
    const insight = response.data.insight;
    let formattedInsight = formatAdvancedInsight(insight);
    addMessage(formattedInsight, false, modelInfo);
}
```

**What happens:**
- Insight displayed in chat
- Formatted with sections (Direct Answer, Key Stats, etc.)
- User sees text response first

---

### Step 8: Chart Generation Prompt (Cursor IDE Style)
**Location:** Frontend (`chart-enhancements.js` → `showChartGenerationPrompt()`)

```javascript
if (response.data.data && response.data.data.length > 0) {
    showChartGenerationPrompt(
        response.data.data,
        response.data.chart_type,
        query
    );
}
```

**What happens:**
- Inline prompt appears in chat
- Shows: "I found X data points. Generate chart?"
- Two buttons: "Skip" and "Generate Chart"

**Visual:**
```
┌─────────────────────────────────────────┐
│ 📊 I found 5 data points.              │
│ Generate chart?                         │
│                                         │
│  [Skip]  [Generate Chart]              │
└─────────────────────────────────────────┘
```

---

### Step 9: User Approval
**Location:** Frontend (`chart-enhancements.js`)

```javascript
// User clicks "Generate Chart"
generateBtn.addEventListener('click', () => {
    promptDiv.querySelector('.chart-prompt-content').innerHTML = 
        '<div class="chart-prompt-result generating">...</div>';
    
    generateEnhancedChart(data, chartType, query);
});
```

**What happens:**
- User clicks "Generate Chart" button
- Prompt updates to "Generating..."
- Chart generation starts

---

### Step 10: Chart Generation
**Location:** Frontend (`chart-enhancements.js` → `generateEnhancedChart()`)

```javascript
function generateEnhancedChart(data, chartType, query) {
    // Create chart container
    const chartCard = document.createElement('div');
    chartCard.className = 'output-card enhanced-chart';
    
    // Initialize ECharts
    const myChart = echarts.init(chartDom, 'dark');
    
    // Configure chart based on type
    const option = getChartOption(data, chartType);
    
    // Render chart
    myChart.setOption(option);
}
```

**What happens:**
1. Creates chart container in workspace
2. Initializes Apache ECharts library
3. Prepares data for visualization
4. Configures chart options (colors, labels, etc.)
5. Renders interactive chart

---

### Step 11: Chart Configuration
**Location:** Frontend (`chart-enhancements.js`)

**For Horizontal Bar Chart:**
```javascript
const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { 
        type: 'category',
        data: ['HDFC Bank', 'SBI', 'ICICI Bank', 'Axis Bank', 'Kotak']
    },
    series: [{
        type: 'bar',
        data: [45000, 38000, 32000, 28000, 25000],
        itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#007acc' },
                { offset: 1, color: '#1e8ad6' }
            ])
        }
    }]
};
```

**Features:**
- Dark theme
- Gradient colors
- Interactive tooltips
- Responsive sizing
- Smooth animations

---

### Step 12: Display Chart
**Location:** Frontend (Workspace)

```javascript
// Insert chart into workspace
workspaceContent.insertBefore(chartCard, workspaceContent.firstChild);

// Add action buttons
chartCard.innerHTML += `
    <div class="chart-actions">
        <button onclick="downloadChart()">Download PNG</button>
        <button onclick="fullscreenChart()">Fullscreen</button>
    </div>
`;
```

**What user sees:**
- Interactive chart in main workspace
- Hover tooltips with data
- Download and fullscreen buttons
- Smooth animations

---

## 🎨 Chart Types & Use Cases

### 1. Horizontal Bar Chart
**When:** Comparing categories (banks, states, types)
**Example:** "Top 5 banks by volume"
```javascript
chartType: "horizontal_bar"
```

### 2. Vertical Bar Chart
**When:** Time series, hourly patterns
**Example:** "Transactions by hour of day"
```javascript
chartType: "vertical_bar"
```

### 3. Line Chart
**When:** Trends over time
**Example:** "Transaction volume over last 7 days"
```javascript
chartType: "line"
```

### 4. Area Chart
**When:** Cumulative trends
**Example:** "Cumulative transaction volume"
```javascript
chartType: "area"
```

### 5. Donut Chart
**When:** Distribution, percentages
**Example:** "Transaction type distribution"
```javascript
chartType: "donut"
```

---

## 📦 Required Components

### Backend Requirements:
```python
# requirements.txt
flask>=3.0.0
pandas>=2.0.0
openai>=1.0.0
```

### Frontend Requirements:
```html
<!-- index_simple.html -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<script src="chart-enhancements.js"></script>
```

### Files Involved:
```
Backend:
├── app_simple.py           # API endpoints
├── advanced_prompts.py     # Query generation & execution
└── multi_llm_service.py    # LLM integration

Frontend:
├── index_simple.html       # HTML structure
├── renderer_simple.js      # Main logic
├── chart-enhancements.js   # Chart generation
└── cursor-style.css        # Styling
```

---

## 🔧 Configuration Options

### Chart Appearance:
```javascript
// chart-enhancements.js

const CHART_CONFIG = {
    theme: 'dark',
    colors: {
        primary: '#007acc',
        secondary: '#1e8ad6',
        success: '#89d185',
        warning: '#cca700',
        error: '#f48771'
    },
    animation: {
        duration: 750,
        easing: 'cubicOut'
    },
    tooltip: {
        backgroundColor: 'rgba(50, 50, 50, 0.95)',
        borderColor: '#007acc',
        borderWidth: 1
    }
};
```

### Data Limits:
```python
# advanced_prompts.py

MAX_CHART_ROWS = 20  # Maximum data points in chart
DEFAULT_LIMIT = 10   # Default number of results
```

---

## 🎯 User Experience Flow

```
1. User asks question
   ↓
2. See "Processing..." indicator
   ↓
3. Receive text insight (2-5 seconds)
   ↓
4. See inline prompt: "Generate chart?"
   ↓
5. Click "Generate Chart"
   ↓
6. See "Generating..." status
   ↓
7. Chart appears in workspace (< 1 second)
   ↓
8. Interact with chart (hover, zoom, download)
```

**Total Time:** 3-7 seconds from query to chart

---

## 🚀 Performance Optimizations

### 1. Lazy Loading
```javascript
// Charts only generated when user approves
if (userClickedGenerate) {
    generateChart();  // Not automatic
}
```

### 2. Data Sampling
```python
# Limit data points for performance
if len(result_df) > 20:
    result_df = result_df.head(20)
```

### 3. GPU Acceleration
```css
/* CSS animations use GPU */
.chart-card {
    transform: translateZ(0);
    will-change: transform;
}
```

### 4. Debounced Resize
```javascript
// Resize charts efficiently
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        myChart.resize();
    }, 250);
});
```

---

## 🐛 Error Handling

### No Data
```javascript
if (!data || data.length === 0) {
    showNotification('No data to visualize', 'warning');
    return;
}
```

### Invalid Chart Type
```javascript
if (!['horizontal_bar', 'vertical_bar', 'line', 'area', 'donut'].includes(chartType)) {
    chartType = 'vertical_bar';  // Default fallback
}
```

### ECharts Not Loaded
```javascript
if (typeof echarts === 'undefined') {
    console.error('ECharts library not loaded');
    showNotification('Chart library not available', 'error');
    return;
}
```

---

## 📊 Example: Complete Flow

### Query: "Show me top 5 banks by transaction volume"

**Step 1-3:** Backend Processing
```
Query → LLM → Query Spec:
{
  "operation": "aggregation",
  "group_by_column": "sender_bank",
  "metrics": ["count"],
  "limit": 5,
  "chart_type": "horizontal_bar"
}
```

**Step 4:** Data Extraction
```
Pandas: df.groupby('sender_bank').size().nlargest(5)
Result: 5 rows
```

**Step 5:** Insight Generation
```
LLM analyzes → Structured insight with recommendations
```

**Step 6-7:** Display Text
```
Chat shows: "HDFC Bank leads with 45,000 transactions..."
```

**Step 8-9:** Chart Prompt
```
Inline prompt: "I found 5 data points. Generate chart?"
User clicks: "Generate Chart"
```

**Step 10-12:** Chart Display
```
ECharts renders horizontal bar chart with:
- 5 banks on Y-axis
- Transaction counts on X-axis
- Gradient blue colors
- Interactive tooltips
- Download/fullscreen buttons
```

**Total Time:** ~5 seconds

---

## 🎓 Summary

### Key Points:

1. **Two-Stage Process:**
   - First: Text insight (always shown)
   - Second: Chart (user approval required)

2. **User Control:**
   - User decides if chart is needed
   - Can skip chart generation
   - Cursor IDE-style inline prompt

3. **Smart Defaults:**
   - LLM suggests best chart type
   - Automatic data preparation
   - Optimized for readability

4. **Performance:**
   - Lazy loading (charts on demand)
   - Data sampling (max 20 points)
   - GPU-accelerated animations

5. **Flexibility:**
   - 5 chart types supported
   - Customizable colors/themes
   - Export capabilities

### Technologies Used:

- **Backend:** Flask, Pandas, OpenAI SDK
- **Frontend:** Vanilla JavaScript, Apache ECharts
- **LLM:** DeepSeek/Gemini for query understanding
- **Visualization:** ECharts 5.4.3

The workflow is designed to be **fast, intuitive, and user-controlled**!
