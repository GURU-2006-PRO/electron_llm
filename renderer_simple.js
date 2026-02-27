const axios = require('axios');

const API_URL = 'http://localhost:5000';
let datasetLoaded = false;

// Query History Management - Now using database
let queryHistory = [];
let historyPanelOpen = false;

// Load history from database on startup
async function loadHistoryFromDatabase() {
    try {
        const response = await axios.get(`${API_URL}/history?limit=50`);
        if (response.data.status === 'success') {
            queryHistory = response.data.history;
            console.log(`Loaded ${queryHistory.length} queries from database`);
        }
    } catch (error) {
        console.error('Failed to load history from database:', error);
        // Fallback to localStorage if database fails
        queryHistory = JSON.parse(localStorage.getItem('queryHistory') || '[]');
    }
}

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
        
        // Initialize dashboard after dataset loads
        if (typeof initializeDashboard === 'function') {
            console.log('Initializing dashboard...');
            initializeDashboard();
        }
        
    } catch (error) {
        console.error('Dataset check failed:', error);
        addMessage('Error: Dataset not loaded. Make sure transactions.csv is in backend/data/', false);
    }
}

// Send message with streaming support
async function sendQuery(query) {
    if (!query.trim()) return;
    
    // Add to history
    addToHistory(query);
    
    addMessage(query, true);
    chatInput.value = '';
    resetTextareaHeight(); // Reset height after sending
    
    // Get selected model
    const selectedModel = modelSelect.value;
    const useAdvanced = advancedMode.checked;
    
    console.log('Using model:', selectedModel, 'Advanced:', useAdvanced);
    
    if (useAdvanced) {
        // Advanced mode - show streaming-like loading effect
        await sendAdvancedQueryWithStreaming(query, selectedModel);
    } else {
        // Simple mode - full streaming
        await sendStreamingQuery(query, selectedModel);
    }
}

// Advanced query with streaming-like effect
async function sendAdvancedQueryWithStreaming(query, model) {
    try {
        console.log('Sending advanced query with streaming effect:', query);
        
        // Show typing indicator
        const typingDiv = showTypingIndicator();
        
        // Show loading skeleton
        const loadingCard = showLoadingSkeleton();
        
        // Choose endpoint
        const endpoint = `${API_URL}/advanced-query`;
        
        const response = await axios.post(endpoint, { 
            query: query,
            model: model 
        });
        
        // Remove typing indicator
        if (typingDiv && typingDiv.parentNode) {
            typingDiv.remove();
        }
        
        // Remove loading skeleton
        if (loadingCard && loadingCard.parentNode) {
            loadingCard.remove();
        }
        
        console.log('Response received:', response.data);
        
        if (response.data.status === 'error') {
            addMessage('Error: ' + (response.data.error || response.data.reason), false);
            if (response.data.suggestion) {
                addMessage('Suggestion: ' + response.data.suggestion, false);
            }
        } else if (response.data.insight) {
            // Advanced mode response with streaming effect
            const insight = response.data.insight;
            const actualModel = response.data.model_used || model;
            
            // Create message div for streaming effect
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message assistant';
            
            // Add model badge
            let modelInfo = '';
            if (model === 'auto') {
                modelInfo = `<div class="model-badge auto" title="Automatically selected based on query complexity">${getModelName(actualModel)} (Auto)</div>`;
            } else {
                modelInfo = `<div class="model-badge">${getModelName(actualModel)}</div>`;
            }
            
            messageDiv.innerHTML = `
                <div class="message-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    ${modelInfo}
                    <div class="streaming-content"></div>
                </div>
            `;
            
            chatMessages.appendChild(messageDiv);
            const streamingContent = messageDiv.querySelector('.streaming-content');
            
            // Simulate streaming effect for direct answer (faster, more natural)
            const directAnswer = insight.direct_answer || '';
            let currentText = '';
            const words = directAnswer.split(' ');
            
            // Stream words in chunks for more natural feel
            const chunkSize = 2; // 2 words at a time
            for (let i = 0; i < words.length; i += chunkSize) {
                const chunk = words.slice(i, i + chunkSize).join(' ');
                currentText += (i > 0 ? ' ' : '') + chunk;
                streamingContent.innerHTML = `<div class="direct-answer">${currentText}<span class="streaming-cursor">▋</span></div>`;
                chatMessages.scrollTop = chatMessages.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 50)); // 50ms per chunk
            }
            
            // Remove cursor
            streamingContent.innerHTML = `<div class="direct-answer">${directAnswer}</div>`;
            
            // Small pause before showing full insight
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Show full formatted insight
            let formattedInsight = formatAdvancedInsight(insight);
            streamingContent.innerHTML = formattedInsight;
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Show reasoning chain if available
            if (response.data.reasoning_chain) {
                showReasoningChain(response.data.reasoning_chain);
            }
            
            // Show data visualization if available
            if (response.data.data && response.data.data.length > 0) {
                // Show inline chart generation prompt (Cursor IDE style)
                const chartType = response.data.chart_type || 'vertical_bar';
                showChartGenerationPrompt(
                    response.data.data,
                    chartType,
                    query
                );
                
                // Always show data table
                showDataTable(response.data.data);
            }
            
        } else if (response.data.answer) {
            // Fallback to simple response
            addMessage(response.data.answer, false);
        }
        
    } catch (error) {
        console.error('Advanced query error:', error);
        addMessage('Error: ' + error.message, false);
    }
}

// Streaming query with real-time token display
async function sendStreamingQuery(query, model) {
    try {
        // Show typing indicator
        const typingDiv = showTypingIndicator();
        
        // Create message container for streaming
        const messageDiv = document.createElement('div');
        messageDiv.className = 'chat-message assistant';
        messageDiv.innerHTML = `
            <div class="message-icon">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content formatted-response">
                <div class="model-badge">${getModelName(model)}</div>
                <div class="message-text streaming-content"></div>
            </div>
        `;
        
        const streamingContent = messageDiv.querySelector('.streaming-content');
        let fullResponse = '';
        
        // Use EventSource for SSE streaming
        const eventSource = new EventSource(`${API_URL}/stream-query?query=${encodeURIComponent(query)}&model=${model}`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'status') {
                // Update typing indicator
                typingDiv.querySelector('.typing-text').textContent = data.message;
            } else if (data.type === 'model') {
                // Update model badge
                const badge = messageDiv.querySelector('.model-badge');
                badge.textContent = `${getModelName(data.model)} (Auto)`;
                badge.classList.add('auto');
            } else if (data.type === 'content') {
                // Remove typing indicator on first content
                if (typingDiv.parentNode) {
                    typingDiv.remove();
                    chatMessages.appendChild(messageDiv);
                }
                
                // Append content with typing effect
                fullResponse += data.content;
                streamingContent.innerHTML = formatStreamingText(fullResponse);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            } else if (data.type === 'done') {
                // Finalize message
                streamingContent.innerHTML = formatText(fullResponse);
                eventSource.close();
            } else if (data.type === 'error') {
                typingDiv.remove();
                addMessage('Error: ' + data.error, false);
                eventSource.close();
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('Streaming error:', error);
            typingDiv.remove();
            addMessage('Streaming connection error. Falling back to standard mode.', false);
            eventSource.close();
            
            // Fallback to non-streaming
            sendAdvancedQuery(query, model);
        };
        
    } catch (error) {
        console.error('Streaming query error:', error);
        addMessage('Error: ' + error.message, false);
    }
}

// Advanced query (non-streaming)
async function sendAdvancedQuery(query, model) {
    try {
        console.log('Sending query:', query);
        
        // Show loading skeleton
        const loadingCard = showLoadingSkeleton();
        
        // Choose endpoint based on mode
        const endpoint = advancedMode.checked ? `${API_URL}/advanced-query` : `${API_URL}/query`;
        
        const response = await axios.post(endpoint, { 
            query: query,
            model: model 
        });
        
        // Remove loading skeleton
        if (loadingCard && loadingCard.parentNode) {
            loadingCard.remove();
        }
        
        console.log('Response received:', response.data);
        
        if (response.data.status === 'error') {
            addMessage('Error: ' + (response.data.error || response.data.reason), false);
            if (response.data.suggestion) {
                addMessage('Suggestion: ' + response.data.suggestion, false);
            }
        } else if (response.data.insight) {
            // Advanced mode response
            const insight = response.data.insight;
            const actualModel = response.data.model_used || model;
            
            // Format advanced insight
            let formattedInsight = formatAdvancedInsight(insight);
            
            // Add model badge
            let modelInfo = '';
            if (model === 'auto') {
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
                // Show inline chart generation prompt (Cursor IDE style)
                const chartType = response.data.chart_type || 'vertical_bar';
                showChartGenerationPrompt(
                    response.data.data,
                    chartType,
                    query
                );
                
                // Always show data table
                showDataTable(response.data.data);
            }
            
        } else if (response.data.answer) {
            // Simple mode response
            const actualModel = response.data.model || model;
            
            let modelInfo = '';
            if (response.data.fallback_used) {
                const originalModel = getModelName(response.data.original_model);
                const fallbackModel = getModelName(response.data.actual_model);
                modelInfo = `<div class="model-badge fallback" title="${originalModel} failed, using ${fallbackModel}">${fallbackModel} (Fallback)</div>`;
            } else if (model === 'auto') {
                modelInfo = `<div class="model-badge auto" title="Automatically selected based on query complexity">${getModelName(actualModel)} (Auto)</div>`;
            } else {
                modelInfo = `<div class="model-badge">${getModelName(actualModel)}</div>`;
            }
            
            addMessage(response.data.answer, false, modelInfo);
            
            // Check if there's data to visualize (even in simple mode)
            if (response.data.data && response.data.data.length > 0) {
                const chartType = response.data.chart_type || 'vertical_bar';
                showChartGenerationPrompt(
                    response.data.data,
                    chartType,
                    query
                );
                showDataTable(response.data.data);
            } else if (query.toLowerCase().includes('top') || 
                       query.toLowerCase().includes('show') ||
                       query.toLowerCase().includes('compare') ||
                       query.toLowerCase().includes('list')) {
                // Suggest enabling advanced mode for data queries
                const suggestionDiv = document.createElement('div');
                suggestionDiv.className = 'chat-message assistant';
                suggestionDiv.innerHTML = `
                    <div class="message-icon">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div class="message-content">
                        <div class="message-text" style="background: rgba(255, 193, 7, 0.1); border-left: 3px solid var(--warning); padding: 12px; border-radius: 6px;">
                            <strong>💡 Tip:</strong> Enable <strong>Advanced Mode</strong> to get structured data and visualizations for this type of query!
                            <br><br>
                            <button onclick="document.getElementById('advancedMode').checked = true; sendQuery('${query.replace(/'/g, "\\'")}');" 
                                    style="background: var(--accent-blue); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-top: 8px;">
                                <i class="fas fa-chart-bar"></i> Retry with Advanced Mode
                            </button>
                        </div>
                    </div>
                `;
                chatMessages.appendChild(suggestionDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
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

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
        <span class="typing-text" style="margin-left: 8px; color: var(--text-secondary); font-size: 12px;">Processing...</span>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return typingDiv;
}

// Show loading skeleton
function showLoadingSkeleton() {
    const card = document.createElement('div');
    card.className = 'output-card';
    card.innerHTML = `
        <div class="output-header">
            <div class="skeleton skeleton-title"></div>
        </div>
        <div class="output-body">
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text"></div>
            <div class="skeleton skeleton-text" style="width: 80%;"></div>
            <div class="skeleton skeleton-chart"></div>
        </div>
    `;
    workspaceContent.insertBefore(card, workspaceContent.firstChild);
    return card;
}

// Format streaming text (with cursor and better formatting)
function formatStreamingText(text) {
    if (!text) return '<span class="streaming-text"></span>';
    
    // Basic markdown-style formatting
    let formatted = text
        // Bold text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Bullet points
        .replace(/^[\-\•\*]\s+(.+)$/gm, '<div class="bullet-point">• $1</div>')
        // Numbers with commas
        .replace(/\b(\d{1,3}(,\d{3})+(\.\d+)?)\b/g, '<span class="number">$1</span>')
        // Percentages
        .replace(/(\d+\.?\d*%)/g, '<span class="percentage">$1</span>');
    
    // Split into paragraphs
    const paragraphs = formatted.split('\n').filter(p => p.trim().length > 0);
    const formattedParagraphs = paragraphs.map(p => {
        if (p.includes('bullet-point')) {
            return p; // Already formatted as bullet
        }
        return `<p>${p}</p>`;
    }).join('');
    
    return formattedParagraphs;
}

// Format final text (same as streaming but without cursor)
function formatText(text) {
    if (!text) return '';
    
    // Basic markdown-style formatting
    let formatted = text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/^[\-\•\*]\s+(.+)$/gm, '<div class="bullet-point">• $1</div>')
        .replace(/\b(\d{1,3}(,\d{3})+(\.\d+)?)\b/g, '<span class="number">$1</span>')
        .replace(/(\d+\.?\d*%)/g, '<span class="percentage">$1</span>');
    
    const paragraphs = formatted.split('\n').filter(p => p.trim().length > 0);
    return paragraphs.map(p => {
        if (p.includes('bullet-point')) {
            return p;
        }
        return `<p>${p}</p>`;
    }).join('');
}

// Add to history (save to database)
async function addToHistory(query) {
    const historyItem = {
        query: query,
        timestamp: Date.now(),
        bookmarked: false
    };
    
    // Add to local array
    queryHistory.unshift(historyItem);
    
    // Keep last 50 in memory
    if (queryHistory.length > 50) {
        queryHistory = queryHistory.slice(0, 50);
    }
    
    // Save to database (async, don't wait)
    try {
        // Note: Database save happens in backend when query is processed
        // This is just for immediate UI update
        localStorage.setItem('queryHistory', JSON.stringify(queryHistory));
    } catch (error) {
        console.error('Failed to save to history:', error);
    }
}

// Toggle bookmark (update database)
async function toggleBookmark(index) {
    const item = queryHistory[index];
    if (!item || !item.id) {
        console.warn('Cannot bookmark item without database ID');
        return;
    }
    
    try {
        const response = await axios.post(`${API_URL}/history/${item.id}/bookmark`);
        if (response.data.status === 'success') {
            queryHistory[index].bookmarked = response.data.bookmarked;
            
            if (historyPanelOpen) {
                showHistoryPanel();
            }
            
            showNotification(
                response.data.bookmarked ? 'Query bookmarked' : 'Bookmark removed',
                'success'
            );
        }
    } catch (error) {
        console.error('Failed to toggle bookmark:', error);
        showNotification('Failed to update bookmark', 'error');
    }
}

// Show history panel
function showHistoryPanel() {
    // Remove existing panel
    const existingPanel = document.querySelector('.history-panel');
    if (existingPanel) {
        existingPanel.remove();
        historyPanelOpen = false;
        return;
    }
    
    historyPanelOpen = true;
    
    const panel = document.createElement('div');
    panel.className = 'history-panel';
    
    let historyHTML = `
        <div class="history-header">
            <span class="history-title">
                <i class="fas fa-history"></i> Query History
            </span>
            <button class="history-clear" onclick="clearHistory()">
                <i class="fas fa-trash"></i> Clear All
            </button>
        </div>
    `;
    
    if (queryHistory.length === 0) {
        historyHTML += '<div class="history-empty">No query history yet</div>';
    } else {
        // Show bookmarked first
        const bookmarked = queryHistory.filter(item => item.bookmarked);
        const regular = queryHistory.filter(item => !item.bookmarked);
        
        if (bookmarked.length > 0) {
            historyHTML += '<div style="padding: 8px 16px; font-size: 11px; color: var(--text-tertiary); font-weight: 600;">BOOKMARKED</div>';
            bookmarked.forEach((item, index) => {
                const actualIndex = queryHistory.indexOf(item);
                historyHTML += createHistoryItem(item, actualIndex);
            });
        }
        
        if (regular.length > 0 && bookmarked.length > 0) {
            historyHTML += '<div style="padding: 8px 16px; font-size: 11px; color: var(--text-tertiary); font-weight: 600;">RECENT</div>';
        }
        
        regular.slice(0, 20).forEach((item, index) => {
            const actualIndex = queryHistory.indexOf(item);
            historyHTML += createHistoryItem(item, actualIndex);
        });
    }
    
    panel.innerHTML = historyHTML;
    
    // Position below chat input
    const inputContainer = document.querySelector('.chat-input-container');
    inputContainer.style.position = 'relative';
    inputContainer.appendChild(panel);
}

// Create history item HTML
function createHistoryItem(item, index) {
    const timeAgo = getTimeAgo(item.timestamp);
    const bookmarkIcon = item.bookmarked ? 'fas fa-star' : 'far fa-star';
    const bookmarkClass = item.bookmarked ? 'bookmarked' : '';
    
    return `
        <div class="history-item" onclick="selectHistoryItem(${index})">
            <div class="history-item-text">${item.query}</div>
            <div class="history-item-time">${timeAgo}</div>
            <button class="history-item-bookmark ${bookmarkClass}" onclick="event.stopPropagation(); toggleBookmark(${index})">
                <i class="${bookmarkIcon}"></i>
            </button>
        </div>
    `;
}

// Select history item
function selectHistoryItem(index) {
    chatInput.value = queryHistory[index].query;
    const panel = document.querySelector('.history-panel');
    if (panel) {
        panel.remove();
        historyPanelOpen = false;
    }
    chatInput.focus();
}

// Clear history (with database)
async function clearHistory() {
    if (confirm('Clear all query history? (Bookmarked queries will be kept)')) {
        try {
            const response = await axios.post(`${API_URL}/history/clear`, {
                keep_bookmarked: true
            });
            
            if (response.data.status === 'success') {
                // Reload history from database
                await loadHistoryFromDatabase();
                showHistoryPanel(); // Refresh panel
                showNotification(`Cleared ${response.data.deleted_count} queries`, 'success');
            }
        } catch (error) {
            console.error('Failed to clear history:', error);
            showNotification('Failed to clear history', 'error');
        }
    }
}

// Get time ago string
function getTimeAgo(timestamp) {
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return new Date(timestamp).toLocaleDateString();
}

// Show notification toast
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Format advanced insight into HTML (flexible, adapts to response structure)
function formatAdvancedInsight(insight) {
    let html = `<div class="advanced-insight">`;
    
    // Direct answer (always present)
    html += `<div class="insight-section">
        <div class="direct-answer">${insight.direct_answer}</div>
    </div>`;
    
    // Key stats (simple questions)
    if (insight.key_stats && insight.key_stats.length > 0) {
        html += `<div class="insight-section">
            <ul class="key-stats">`;
        insight.key_stats.forEach(stat => {
            html += `<li>${stat}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Key insights (analysis questions)
    if (insight.key_insights && insight.key_insights.length > 0) {
        html += `<div class="insight-section">
            <ul class="key-stats">`;
        insight.key_insights.forEach(stat => {
            html += `<li>${stat}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Comparison details (comparison questions)
    if (insight.comparison_details) {
        html += `<div class="insight-section comparison-box">
            <div class="comparison-grid">`;
        for (const [key, value] of Object.entries(insight.comparison_details)) {
            html += `<div class="comparison-item">
                <span class="comparison-label">${key.replace(/_/g, ' ')}</span>
                <span class="comparison-value">${value}</span>
            </div>`;
        }
        html += `</div></div>`;
    }
    
    // Contributing factors (why questions)
    if (insight.contributing_factors && insight.contributing_factors.length > 0) {
        html += `<div class="insight-section">
            <h4>Contributing Factors:</h4>
            <ul class="contributing-factors">`;
        insight.contributing_factors.forEach(factor => {
            html += `<li>${factor}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Evidence (why questions)
    if (insight.evidence) {
        html += `<div class="insight-section">
            <h4>Evidence:</h4>
            <p>${insight.evidence}</p>
        </div>`;
    }
    
    // Pattern (analysis questions)
    if (insight.pattern) {
        html += `<div class="insight-section">
            <h4>Pattern:</h4>
            <p>${insight.pattern}</p>
        </div>`;
    }
    
    // Root cause
    if (insight.root_cause) {
        html += `<div class="insight-section">
            <h4>Root Cause:</h4>
            <p>${insight.root_cause}</p>
        </div>`;
    }
    
    // Business impact (analysis questions)
    if (insight.business_impact) {
        html += `<div class="insight-section impact-box">
            <h4>Business Impact:</h4>
            <div class="impact-grid">`;
        for (const [key, value] of Object.entries(insight.business_impact)) {
            const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `<div class="impact-item">
                <span class="impact-label">${label}</span>
                <span class="impact-value">${value}</span>
            </div>`;
        }
        html += `</div></div>`;
    }
    
    // Recommendation (if present)
    if (insight.recommendation) {
        const rec = insight.recommendation;
        html += `<div class="insight-section recommendation-box">
            <h4>💡 Recommendation:</h4>`;
        
        if (typeof rec === 'string') {
            html += `<p>${rec}</p>`;
        } else if (typeof rec === 'object') {
            if (rec.action) html += `<p><strong>Action:</strong> ${rec.action}</p>`;
            if (rec.what) html += `<p><strong>What:</strong> ${rec.what}</p>`;
            if (rec.how) html += `<p><strong>How:</strong> ${rec.how}</p>`;
            if (rec.expected_improvement) html += `<p><strong>Expected Impact:</strong> ${rec.expected_improvement}</p>`;
            if (rec.implementation) html += `<p><strong>Timeline:</strong> <span class="priority-badge">${rec.implementation}</span></p>`;
            if (rec.priority) html += `<p><strong>Priority:</strong> <span class="priority-badge">${rec.priority}</span></p>`;
            if (rec.owner) html += `<p><strong>Owner:</strong> ${rec.owner}</p>`;
        }
        html += `</div>`;
    }
    
    // Data limitations (if present)
    if (insight.data_limitations) {
        html += `<div class="insight-section limitations">
            <h4>⚠️ Data Limitations:</h4>
            <p>${insight.data_limitations}</p>
        </div>`;
    }
    
    // Follow-up questions (if present)
    if (insight.follow_up_questions && insight.follow_up_questions.length > 0) {
        html += `<div class="insight-section">
            <h4>💭 Follow-Up Questions:</h4>
            <ul class="follow-up-questions">`;
        insight.follow_up_questions.forEach(q => {
            html += `<li class="clickable-question" onclick="askFollowUp('${q.replace(/'/g, "\\'")}')">${q}</li>`;
        });
        html += `</ul></div>`;
    }
    
    // Confidence (always show if present)
    if (insight.confidence) {
        const confidenceClass = insight.confidence.toLowerCase();
        html += `<div class="insight-section confidence-box">
            <span class="confidence-badge ${confidenceClass}">${insight.confidence} Confidence</span>
            ${insight.confidence_reason ? `<span class="confidence-reason"> — ${insight.confidence_reason}</span>` : ''}
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

// Auto-expand textarea as user types
chatInput.addEventListener('input', function() {
    // Reset height to auto to get the correct scrollHeight
    this.style.height = 'auto';
    
    // Set height based on content, respecting min and max
    const newHeight = Math.min(Math.max(this.scrollHeight, 42), 315);
    this.style.height = newHeight + 'px';
    
    // Show/hide scrollbar based on content
    if (this.scrollHeight > 315) {
        this.style.overflowY = 'auto';
    } else {
        this.style.overflowY = 'hidden';
    }
});

// Reset textarea height after sending
function resetTextareaHeight() {
    chatInput.style.height = 'auto';
    chatInput.style.overflowY = 'hidden';
}

// Initialize
checkConnection();
setInterval(checkConnection, 5000);

// Load history from database
loadHistoryFromDatabase();

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
            case 'h':
                e.preventDefault();
                showHistoryPanel();
                break;
            case 'b':
                e.preventDefault();
                if (queryHistory.length > 0) {
                    toggleBookmark(0);
                    showNotification('Bookmarked last query', 'success');
                }
                break;
        }
    }
    
    // Escape to close history panel
    if (e.key === 'Escape') {
        const panel = document.querySelector('.history-panel');
        if (panel) {
            panel.remove();
            historyPanelOpen = false;
        }
    }
});

console.log('All icon actions loaded');


// Drag-to-Resize Sidebar Functionality
const leftSidebar = document.getElementById('leftSidebar');
const rightSidebar = document.getElementById('rightSidebar');
const leftResize = document.getElementById('leftResize');
const rightResize = document.getElementById('rightResize');

console.log('Resize elements:', {
    leftSidebar: !!leftSidebar,
    rightSidebar: !!rightSidebar,
    leftResize: !!leftResize,
    rightResize: !!rightResize
});

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
    console.log('Started resizing:', resizer);
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
        console.log('Stopped resizing');
        currentResizer = null;
        document.body.classList.remove('resizing');
    }
}

// Event listeners for left resize handle
if (leftResize) {
    leftResize.addEventListener('mousedown', (e) => startResize(e, 'left'));
    console.log('Left resize handle attached');
}

// Event listeners for right resize handle
if (rightResize) {
    rightResize.addEventListener('mousedown', (e) => startResize(e, 'right'));
    console.log('Right resize handle attached');
}

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
