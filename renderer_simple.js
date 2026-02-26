const axios = require('axios');

const API_URL = 'http://localhost:5000';
let datasetLoaded = false;

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendMessage');
const statusDot = document.getElementById('connectionStatus');
const statusText = document.getElementById('statusText');
const workspaceContent = document.getElementById('workspaceContent');
const modelSelect = document.getElementById('modelSelect');
const advancedMode = document.getElementById('advancedMode');

// Check connection
async function checkConnection() {
    try {
        await axios.get(`${API_URL}/health`);
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } catch (error) {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

// Auto-load dataset on startup
async function autoLoadDataset() {
    try {
        console.log('Checking dataset status...');
        
        // Get columns from backend (dataset is already loaded)
        const response = await axios.get(`${API_URL}/columns`);
        
        datasetLoaded = true;
        
        // Update workspace
        workspaceContent.innerHTML = `
            <div class="output-card">
                <div class="output-header">
                    <div class="output-title">Dataset Ready</div>
                </div>
                <div class="output-body">
                    <p>Transaction data loaded and ready for analysis</p>
                    <div class="stat-grid">
                        <div class="stat-item">
                            <div class="stat-label">Records</div>
                            <div class="stat-value">${response.data.rows.toLocaleString()}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">Columns</div>
                            <div class="stat-value">${response.data.columns.length}</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        addMessage('Dataset loaded! Ask me questions about your transaction data.', false);
        console.log('Dataset ready:', response.data.rows, 'rows');
        
    } catch (error) {
        console.error('Dataset check failed:', error);
        addMessage('Error: Dataset not loaded. Make sure transactions.csv is in backend/data/', false);
    }
}

// Send message
async function sendQuery(query) {
    if (!query.trim()) return;
    
    addMessage(query, true);
    chatInput.value = '';
    
    // Get selected model
    const selectedModel = modelSelect.value;
    const useAdvanced = advancedMode.checked;
    console.log('Using model:', selectedModel, 'Advanced:', useAdvanced);
    
    try {
        console.log('Sending query:', query);
        
        // Choose endpoint based on mode
        const endpoint = useAdvanced ? `${API_URL}/advanced-query` : `${API_URL}/query`;
        
        const response = await axios.post(endpoint, { 
            query: query,
            model: selectedModel 
        });
        console.log('Response received:', response.data);
        
        if (response.data.status === 'error') {
            addMessage('Error: ' + (response.data.error || response.data.reason), false);
            if (response.data.suggestion) {
                addMessage('Suggestion: ' + response.data.suggestion, false);
            }
        } else if (response.data.insight) {
            // Advanced mode response
            const insight = response.data.insight;
            const actualModel = response.data.model_used || selectedModel;
            
            // Format advanced insight
            let formattedInsight = formatAdvancedInsight(insight);
            
            // Add model badge
            let modelInfo = '';
            if (selectedModel === 'auto') {
                modelInfo = `<div class="model-badge auto" title="Automatically selected based on query complexity">${getModelName(actualModel)} (Auto)</div>`;
            } else {
                modelInfo = `<div class="model-badge">${getModelName(actualModel)}</div>`;
            }
            
            addMessage(formattedInsight, false, modelInfo);
            
            // Show reasoning chain if available
            if (response.data.reasoning_chain) {
                showReasoningChain(response.data.reasoning_chain);
            }
            
            // Show data visualization if available
            if (response.data.data && response.data.data.length > 0) {
                // Render chart first
                const chartType = response.data.chart_type || 'vertical_bar';
                renderChart(response.data.data, chartType, {
                    title: user_question,
                    seriesName: response.data.intent || 'Analysis'
                });
                
                // Then show data table
                showDataTable(response.data.data);
            }
            
        } else if (response.data.answer) {
            // Simple mode response
            const actualModel = response.data.model || selectedModel;
            
            let modelInfo = '';
            if (response.data.fallback_used) {
                const originalModel = getModelName(response.data.original_model);
                const fallbackModel = getModelName(response.data.actual_model);
                modelInfo = `<div class="model-badge fallback" title="${originalModel} failed, using ${fallbackModel}">${fallbackModel} (Fallback)</div>`;
            } else if (selectedModel === 'auto') {
                modelInfo = `<div class="model-badge auto" title="Automatically selected based on query complexity">${getModelName(actualModel)} (Auto)</div>`;
            } else {
                modelInfo = `<div class="model-badge">${getModelName(actualModel)}</div>`;
            }
            
            addMessage(response.data.answer, false, modelInfo);
        } else {
            addMessage('No response received from server', false);
        }
        
        if (response.data.statistics) {
            showStatistics(response.data.statistics);
        }
    } catch (error) {
        console.error('Query error:', error);
        addMessage('Error: ' + error.message, false);
    }
}

// Format advanced insight into HTML
function formatAdvancedInsight(insight) {
    let html = `<div class="advanced-insight">`;
    
    // Direct answer
    html += `<div class="insight-section">
        <h3>📊 Direct Answer</h3>
        <p class="direct-answer">${insight.direct_answer}</p>
    </div>`;
    
    // Key stats
    if (insight.key_stats && insight.key_stats.length > 0) {
        html += `<div class="insight-section">
            <h3>🔑 Key Statistics</h3>
            <ul class="key-stats">`;
        insight.key_stats.forEach(stat => {
            html += `<li>${stat}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Pattern
    if (insight.pattern) {
        html += `<div class="insight-section">
            <h3>📈 Pattern Identified</h3>
            <p>${insight.pattern}</p>
        </div>`;
    }
    
    // Root cause
    if (insight.root_cause) {
        html += `<div class="insight-section">
            <h3>🔍 Root Cause Analysis</h3>
            <p>${insight.root_cause}</p>
        </div>`;
    }
    
    // Business impact
    if (insight.business_impact) {
        html += `<div class="insight-section">
            <h3>💼 Business Impact</h3>
            <ul class="business-impact">`;
        for (const [key, value] of Object.entries(insight.business_impact)) {
            html += `<li><strong>${key.replace(/_/g, ' ')}:</strong> ${value}</li>`;
        }
        html += `</ul></div>`;
    }
    
    // Recommendation
    if (insight.recommendation) {
        html += `<div class="insight-section recommendation">
            <h3>💡 Recommendation</h3>
            <p><strong>What:</strong> ${insight.recommendation.what}</p>
            <p><strong>How:</strong> ${insight.recommendation.how}</p>
            <p><strong>Expected Impact:</strong> ${insight.recommendation.expected_improvement}</p>
            <p><strong>Priority:</strong> <span class="priority-badge">${insight.recommendation.priority}</span></p>
            <p><strong>Owner:</strong> ${insight.recommendation.owner}</p>
        </div>`;
    }
    
    // Follow-up questions
    if (insight.follow_up_questions && insight.follow_up_questions.length > 0) {
        html += `<div class="insight-section">
            <h3>❓ Follow-Up Questions</h3>
            <ul class="follow-up-questions">`;
        insight.follow_up_questions.forEach(q => {
            html += `<li class="clickable-question" onclick="askFollowUp('${q.replace(/'/g, "\\'")}')">${q}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Confidence
    if (insight.confidence) {
        const confidenceClass = insight.confidence.toLowerCase();
        html += `<div class="insight-section confidence">
            <h3>✓ Confidence Level</h3>
            <p><span class="confidence-badge ${confidenceClass}">${insight.confidence}</span></p>
            <p class="confidence-reason">${insight.confidence_reason}</p>
        </div>`;
    }
    
    html += `</div>`;
    return html;
}

// Show reasoning chain in workspace
function showReasoningChain(reasoning) {
    const card = document.createElement('div');
    card.className = 'output-card reasoning-card';
    card.innerHTML = `
        <div class="output-header">
            <div class="output-title">🧠 AI Reasoning Process (DeepSeek R1)</div>
        </div>
        <div class="output-body">
            <pre class="reasoning-content">${reasoning}</pre>
        </div>
    `;
    workspaceContent.insertBefore(card, workspaceContent.firstChild);
}

// Show data table
function showDataTable(data) {
    if (!data || data.length === 0) return;
    
    const columns = Object.keys(data[0]);
    let tableHTML = `<table class="data-table">
        <thead><tr>`;
    
    columns.forEach(col => {
        tableHTML += `<th>${col}</th>`;
    });
    tableHTML += `</tr></thead><tbody>`;
    
    data.forEach(row => {
        tableHTML += `<tr>`;
        columns.forEach(col => {
            let value = row[col];
            if (typeof value === 'number') {
                value = value.toLocaleString(undefined, {maximumFractionDigits: 2});
            }
            tableHTML += `<td>${value}</td>`;
        });
        tableHTML += `</tr>`;
    });
    
    tableHTML += `</tbody></table>`;
    
    const card = document.createElement('div');
    card.className = 'output-card';
    card.innerHTML = `
        <div class="output-header">
            <div class="output-title">📋 Query Results (${data.length} rows)</div>
        </div>
        <div class="output-body">
            ${tableHTML}
        </div>
    `;
    workspaceContent.insertBefore(card, workspaceContent.firstChild);
}

// Render ECharts visualization
function renderChart(data, chartType, chartConfig) {
    if (!data || data.length === 0) return;
    
    // Create chart container
    const chartCard = document.createElement('div');
    chartCard.className = 'output-card chart-card';
    const chartId = 'chart-' + Date.now();
    chartCard.innerHTML = `
        <div class="output-header">
            <div class="output-title">📊 Visualization</div>
        </div>
        <div class="output-body">
            <div id="${chartId}" class="echart-container"></div>
        </div>
    `;
    workspaceContent.insertBefore(chartCard, workspaceContent.firstChild);
    
    // Initialize ECharts
    const chartDom = document.getElementById(chartId);
    const myChart = echarts.init(chartDom, 'dark');
    
    // Prepare data based on chart type
    let option = {};
    
    if (chartType === 'horizontal_bar' || chartType === 'vertical_bar') {
        // Bar chart
        const categories = data.map(row => row[Object.keys(row)[0]]);
        const values = data.map(row => {
            // Find numeric column
            for (let key in row) {
                if (typeof row[key] === 'number' && key !== 'total_count') {
                    return row[key];
                }
            }
            return row[Object.keys(row)[1]];
        });
        
        option = {
            title: {
                text: chartConfig?.title || 'Analysis Results',
                left: 'center',
                textStyle: { color: '#cccccc' }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' }
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: chartType === 'horizontal_bar' ? {
                type: 'value',
                axisLabel: { color: '#858585' }
            } : {
                type: 'category',
                data: categories,
                axisLabel: { 
                    color: '#858585',
                    rotate: 45
                }
            },
            yAxis: chartType === 'horizontal_bar' ? {
                type: 'category',
                data: categories,
                axisLabel: { color: '#858585' }
            } : {
                type: 'value',
                axisLabel: { color: '#858585' }
            },
            series: [{
                name: chartConfig?.seriesName || 'Value',
                type: 'bar',
                data: values,
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#007acc' },
                        { offset: 1, color: '#1e8ad6' }
                    ])
                },
                label: {
                    show: true,
                    position: chartType === 'horizontal_bar' ? 'right' : 'top',
                    formatter: '{c}',
                    color: '#cccccc'
                }
            }]
        };
    } else if (chartType === 'line' || chartType === 'area') {
        // Line/Area chart
        const categories = data.map(row => row[Object.keys(row)[0]]);
        const values = data.map(row => {
            for (let key in row) {
                if (typeof row[key] === 'number' && key !== 'total_count') {
                    return row[key];
                }
            }
            return row[Object.keys(row)[1]];
        });
        
        option = {
            title: {
                text: chartConfig?.title || 'Trend Analysis',
                left: 'center',
                textStyle: { color: '#cccccc' }
            },
            tooltip: {
                trigger: 'axis'
            },
            grid: {
                left: '3%',
                right: '4%',
                bottom: '3%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: categories,
                axisLabel: { color: '#858585' }
            },
            yAxis: {
                type: 'value',
                axisLabel: { color: '#858585' }
            },
            series: [{
                name: chartConfig?.seriesName || 'Value',
                type: 'line',
                data: values,
                smooth: true,
                areaStyle: chartType === 'area' ? {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(0, 122, 204, 0.5)' },
                        { offset: 1, color: 'rgba(0, 122, 204, 0.1)' }
                    ])
                } : null,
                itemStyle: { color: '#007acc' },
                lineStyle: { width: 3 }
            }]
        };
    } else if (chartType === 'donut') {
        // Donut/Pie chart
        const pieData = data.map(row => ({
            name: row[Object.keys(row)[0]],
            value: (() => {
                for (let key in row) {
                    if (typeof row[key] === 'number') {
                        return row[key];
                    }
                }
                return 0;
            })()
        }));
        
        option = {
            title: {
                text: chartConfig?.title || 'Distribution',
                left: 'center',
                textStyle: { color: '#cccccc' }
            },
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            legend: {
                orient: 'vertical',
                left: 'left',
                textStyle: { color: '#858585' }
            },
            series: [{
                name: chartConfig?.seriesName || 'Distribution',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#252526',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    formatter: '{b}: {d}%',
                    color: '#cccccc'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 16,
                        fontWeight: 'bold'
                    }
                },
                data: pieData
            }]
        };
    }
    
    // Set option and render
    myChart.setOption(option);
    
    // Responsive resize
    window.addEventListener('resize', () => {
        myChart.resize();
    });
}

// Ask follow-up question
function askFollowUp(question) {
    chatInput.value = question;
    sendQuery(question);
}

// Get friendly model name
function getModelName(modelValue) {
    const modelNames = {
        'auto': 'Auto',
        'deepseek-r1': 'DeepSeek R1',
        'deepseek-chat': 'DeepSeek Chat',
        'gemini-flash': 'Gemini 2.5 Flash',
        'gemini-pro': 'Gemini Pro',
        'deepseek/deepseek-r1': 'DeepSeek R1',
        'deepseek/deepseek-chat': 'DeepSeek Chat',
        'anthropic/claude-3-haiku': 'Claude 3 Haiku',
        'meta-llama/llama-3.1-8b-instruct': 'Llama 3.1'
    };
    return modelNames[modelValue] || modelValue;
}

// Add message
function addMessage(text, isUser, modelInfo = '') {
    console.log('Adding message:', { text: text.substring(0, 100), isUser });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'assistant'}`;
    
    // Format bot messages with HTML if they contain formatting
    let formattedText = text;
    if (!isUser && (text.includes('<') || text.includes('>'))) {
        // It's already HTML formatted
        formattedText = text;
    } else {
        // Convert plain text line breaks, filter out empty paragraphs
        const paragraphs = text.split('\n').filter(p => p.trim().length > 0);
        formattedText = paragraphs.map(p => `<p>${p}</p>`).join('');
    }
    
    messageDiv.innerHTML = `
        <div class="message-icon">
            <i class="fas fa-${isUser ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content formatted-response">
            ${modelInfo}
            <div class="message-text">
                ${formattedText}
            </div>
        </div>
    `;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show statistics
function showStatistics(stats) {
    const statsHTML = Object.entries(stats).map(([key, value]) => `
        <div class="stat-item">
            <div class="stat-label">${key}</div>
            <div class="stat-value">${value}</div>
        </div>
    `).join('');
    
    const card = document.createElement('div');
    card.className = 'output-card';
    card.innerHTML = `
        <div class="output-header">
            <div class="output-title">Statistics</div>
        </div>
        <div class="output-body">
            <div class="stat-grid">${statsHTML}</div>
        </div>
    `;
    
    workspaceContent.insertBefore(card, workspaceContent.firstChild);
}

// Event listeners
sendBtn.addEventListener('click', () => sendQuery(chatInput.value));
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery(chatInput.value);
    }
});

// Initialize
checkConnection();
setInterval(checkConnection, 5000);

// Auto-load dataset after 1 second
setTimeout(autoLoadDataset, 1000);

// Restore model selection from localStorage
const savedModel = localStorage.getItem('selectedModel');
if (savedModel && modelSelect) {
    modelSelect.value = savedModel;
}

// Save model selection when changed
if (modelSelect) {
    modelSelect.addEventListener('change', () => {
        localStorage.setItem('selectedModel', modelSelect.value);
        console.log('Model changed to:', modelSelect.value);
    });
}

console.log('Simple renderer loaded');


// Import icon actions
const IconActions = require('./features/icon-actions.js');
const iconActions = new IconActions(axios);

// Initialize theme on load
iconActions.initTheme();

// Top Bar Icon Actions
document.getElementById('refreshBtn')?.addEventListener('click', () => {
    iconActions.refreshData();
    autoLoadDataset();
});

document.getElementById('exportBtn')?.addEventListener('click', () => iconActions.exportResults());
document.getElementById('reportBtn')?.addEventListener('click', () => iconActions.generateReport());
document.getElementById('searchBtn')?.addEventListener('click', () => iconActions.showSearch());
document.getElementById('clearWorkspaceBtn')?.addEventListener('click', () => iconActions.clearWorkspace());
document.getElementById('settingsBtn')?.addEventListener('click', () => iconActions.showSettings());
document.getElementById('helpBtn')?.addEventListener('click', () => iconActions.showHelp());
document.getElementById('themeBtn')?.addEventListener('click', () => iconActions.toggleTheme());

// Chat Action Icons
document.getElementById('clearChatBtn')?.addEventListener('click', () => iconActions.clearChat());
document.getElementById('saveChatBtn')?.addEventListener('click', () => iconActions.saveConversation());
document.getElementById('favoritesBtn')?.addEventListener('click', () => iconActions.showFavorites());

// Input Action Icons
document.getElementById('attachBtn')?.addEventListener('click', () => iconActions.attachFile());
document.getElementById('voiceBtn')?.addEventListener('click', () => iconActions.voiceInput());
document.getElementById('quickStatsBtn')?.addEventListener('click', () => iconActions.quickStats());

// Column Action Icons
document.getElementById('filterColumnsBtn')?.addEventListener('click', () => {
    iconActions.showNotification('Column filtering coming soon', 'info');
});

document.getElementById('searchColumnsBtn')?.addEventListener('click', () => {
    iconActions.showNotification('Column search coming soon', 'info');
});

// Add result card actions to new cards
function addResultCardActions(card) {
    const header = card.querySelector('.output-header');
    if (!header || header.querySelector('.result-card-actions')) return;

    const actions = document.createElement('div');
    actions.className = 'result-card-actions';
    actions.innerHTML = `
        <button class="result-action-btn pin" title="Pin Result">
            <i class="fas fa-thumbtack"></i>
        </button>
        <button class="result-action-btn copy" title="Copy">
            <i class="fas fa-copy"></i>
        </button>
        <button class="result-action-btn download" title="Download">
            <i class="fas fa-download"></i>
        </button>
        <button class="result-action-btn close" title="Close">
            <i class="fas fa-times"></i>
        </button>
    `;

    header.appendChild(actions);

    // Add event listeners
    actions.querySelector('.pin').addEventListener('click', () => iconActions.pinResult(card));
    actions.querySelector('.copy').addEventListener('click', () => iconActions.copyResult(card));
    actions.querySelector('.download').addEventListener('click', () => iconActions.downloadResult(card));
    actions.querySelector('.close').addEventListener('click', () => iconActions.closeResult(card));
}

// Update showStatistics to add actions
const originalShowStatistics = showStatistics;
showStatistics = function(stats) {
    originalShowStatistics(stats);
    const cards = document.querySelectorAll('.output-card');
    cards.forEach(card => addResultCardActions(card));
};

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key.toLowerCase()) {
            case 'r':
                e.preventDefault();
                iconActions.refreshData();
                break;
            case 'e':
                e.preventDefault();
                iconActions.exportResults();
                break;
            case 'k':
                e.preventDefault();
                iconActions.showSearch();
                break;
        }
    }
});

console.log('All icon actions loaded');


// Drag-to-Resize Sidebar Functionality
const leftSidebar = document.getElementById('leftSidebar');
const rightSidebar = document.getElementById('rightSidebar');
const leftResize = document.getElementById('leftResize');
const rightResize = document.getElementById('rightResize');

let isResizing = false;
let currentResizer = null;

// Minimum and maximum widths
const MIN_SIDEBAR_WIDTH = 200;
const MAX_SIDEBAR_WIDTH = 600;

// Start resizing
function startResize(e, resizer) {
    isResizing = true;
    currentResizer = resizer;
    document.body.classList.add('resizing');
    e.preventDefault();
}

// Perform resize
function resize(e) {
    if (!isResizing) return;

    if (currentResizer === 'left') {
        const newWidth = e.clientX;
        if (newWidth >= MIN_SIDEBAR_WIDTH && newWidth <= MAX_SIDEBAR_WIDTH) {
            leftSidebar.style.width = newWidth + 'px';
            localStorage.setItem('leftSidebarWidth', newWidth);
        }
    } else if (currentResizer === 'right') {
        const newWidth = window.innerWidth - e.clientX;
        if (newWidth >= MIN_SIDEBAR_WIDTH && newWidth <= MAX_SIDEBAR_WIDTH) {
            rightSidebar.style.width = newWidth + 'px';
            localStorage.setItem('rightSidebarWidth', newWidth);
        }
    }
}

// Stop resizing
function stopResize() {
    if (isResizing) {
        isResizing = false;
        currentResizer = null;
        document.body.classList.remove('resizing');
    }
}

// Event listeners for left resize handle
leftResize.addEventListener('mousedown', (e) => startResize(e, 'left'));

// Event listeners for right resize handle
rightResize.addEventListener('mousedown', (e) => startResize(e, 'right'));

// Global mouse move and up listeners
document.addEventListener('mousemove', resize);
document.addEventListener('mouseup', stopResize);

// Restore sidebar widths from localStorage
function restoreSidebarWidths() {
    const leftWidth = localStorage.getItem('leftSidebarWidth');
    const rightWidth = localStorage.getItem('rightSidebarWidth');
    
    if (leftWidth) {
        const width = parseInt(leftWidth);
        if (width >= MIN_SIDEBAR_WIDTH && width <= MAX_SIDEBAR_WIDTH) {
            leftSidebar.style.width = width + 'px';
        }
    }
    
    if (rightWidth) {
        const width = parseInt(rightWidth);
        if (width >= MIN_SIDEBAR_WIDTH && width <= MAX_SIDEBAR_WIDTH) {
            rightSidebar.style.width = width + 'px';
        }
    }
}

// Restore widths on load
restoreSidebarWidths();

console.log('Drag-to-resize functionality loaded');
console.log('Drag the edges between sidebars and workspace to resize');
