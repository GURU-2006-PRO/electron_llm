// Icon Actions - All functionality for toolbar icons

class IconActions {
    constructor(api) {
        this.api = api;
        this.pinnedResults = new Set();
        this.favorites = [];
        this.theme = 'dark';
    }

    // Top Bar Actions
    async refreshData() {
        const btn = document.getElementById('refreshBtn');
        const icon = btn.querySelector('i');
        icon.classList.add('fa-spin');
        
        try {
            const response = await this.api.post('/load-data');
            if (response.data.success) {
                this.showNotification('Data refreshed successfully', 'success');
            }
        } catch (error) {
            this.showNotification('Failed to refresh data', 'error');
        } finally {
            icon.classList.remove('fa-spin');
        }
    }

    async exportResults() {
        // Check if there's data to export
        const dataTable = document.querySelector('.data-table');
        if (!dataTable) {
            this.showNotification('No data to export. Ask a question first!', 'warning');
            return;
        }

        // Extract table data
        const headers = [];
        const rows = [];
        
        // Get headers
        dataTable.querySelectorAll('thead th').forEach(th => {
            headers.push(th.textContent.trim());
        });
        
        // Get rows
        dataTable.querySelectorAll('tbody tr').forEach(tr => {
            const row = [];
            tr.querySelectorAll('td').forEach(td => {
                row.push(td.textContent.trim());
            });
            rows.push(row);
        });

        // Create CSV content
        let csvContent = headers.join(',') + '\n';
        rows.forEach(row => {
            // Escape commas and quotes in data
            const escapedRow = row.map(cell => {
                if (cell.includes(',') || cell.includes('"') || cell.includes('\n')) {
                    return `"${cell.replace(/"/g, '""')}"`;
                }
                return cell;
            });
            csvContent += escapedRow.join(',') + '\n';
        });

        // Download CSV
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `insightx-data-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification(`Exported ${rows.length} rows to CSV`, 'success');
    }

    async generateReport() {
        this.showNotification('Generating report...', 'info');
        
        // Collect all insights from chat
        const insights = [];
        document.querySelectorAll('.chat-message.assistant').forEach(msg => {
            const text = msg.querySelector('.message-text')?.innerHTML;
            if (text && !text.includes('Dataset loaded') && !text.includes('Ask me')) {
                insights.push(text);
            }
        });

        // Get data table if exists
        let dataTableHTML = '';
        const dataTable = document.querySelector('.data-table');
        if (dataTable) {
            dataTableHTML = `
                <div class="section">
                    <h2>📊 Data Results</h2>
                    ${dataTable.outerHTML}
                </div>
            `;
        }

        // Get charts if exist
        let chartsHTML = '';
        const charts = document.querySelectorAll('.chart-card');
        if (charts.length > 0) {
            chartsHTML = '<div class="section"><h2>📈 Visualizations</h2>';
            charts.forEach((chart, index) => {
                const title = chart.querySelector('.output-title')?.textContent || `Chart ${index + 1}`;
                const chartId = chart.querySelector('.echart-container')?.id;
                
                if (chartId && window.chartRegistry && window.chartRegistry[chartId]) {
                    // Get chart as base64 image
                    const chartInstance = window.chartRegistry[chartId];
                    const imageData = chartInstance.getDataURL({
                        type: 'png',
                        pixelRatio: 2,
                        backgroundColor: '#ffffff'
                    });
                    chartsHTML += `
                        <div class="chart-section">
                            <h3>${title}</h3>
                            <img src="${imageData}" style="max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 8px;">
                        </div>
                    `;
                }
            });
            chartsHTML += '</div>';
        }

        // Create comprehensive HTML report
        const html = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>InsightX Analytics Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007acc;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .header .meta {
            color: #666;
            font-size: 14px;
        }
        .section {
            margin: 30px 0;
            padding: 20px 0;
            border-bottom: 1px solid #eee;
        }
        .section:last-child {
            border-bottom: none;
        }
        .section h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section h3 {
            color: #555;
            font-size: 18px;
            margin: 20px 0 10px 0;
        }
        .insight-box {
            background: #f8f9fa;
            border-left: 4px solid #007acc;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .insight-box ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        .insight-box li {
            margin: 5px 0;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 14px;
        }
        .data-table th {
            background: #007acc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #eee;
        }
        .data-table tr:hover {
            background: #f8f9fa;
        }
        .chart-section {
            margin: 20px 0;
            page-break-inside: avoid;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            text-align: center;
            color: #666;
            font-size: 12px;
        }
        @media print {
            body { background: white; padding: 0; }
            .container { box-shadow: none; }
            .section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 InsightX Analytics Report</h1>
            <div class="meta">
                Generated: ${new Date().toLocaleString()}<br>
                Dataset: UPI Transactions 2024 (250,000 records)
            </div>
        </div>

        ${insights.length > 0 ? `
        <div class="section">
            <h2>💡 Key Insights</h2>
            ${insights.map((insight, i) => `
                <div class="insight-box">
                    <strong>Analysis ${i + 1}:</strong>
                    ${insight}
                </div>
            `).join('')}
        </div>
        ` : ''}

        ${chartsHTML}
        
        ${dataTableHTML}

        <div class="footer">
            <p><strong>InsightX Analytics</strong> - AI-Powered Data Analysis Platform</p>
            <p>This report was automatically generated from your analysis session.</p>
        </div>
    </div>
</body>
</html>`;

        // Download HTML report
        const blob = new Blob([html], { type: 'text/html;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `insightx-report-${new Date().toISOString().split('T')[0]}.html`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Report generated successfully! Open in browser to print as PDF.', 'success');
    }

    showSearch() {
        const modal = this.createModal('Search', `
            <input type="text" id="searchInput" placeholder="Search in results..." 
                   style="width: 100%; padding: 10px; background: var(--bg-tertiary); 
                          border: 1px solid var(--border-color); border-radius: 6px; 
                          color: var(--text-primary); font-size: 14px;">
            <div id="searchResults" style="margin-top: 16px; max-height: 300px; overflow-y: auto;"></div>
        `);

        const searchInput = modal.querySelector('#searchInput');
        const searchResults = modal.querySelector('#searchResults');

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            if (!query) {
                searchResults.innerHTML = '';
                return;
            }

            const results = [];
            document.querySelectorAll('.output-card').forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(query)) {
                    const title = card.querySelector('.output-title')?.textContent;
                    results.push(title);
                }
            });

            searchResults.innerHTML = results.length > 0
                ? results.map(r => `<div style="padding: 8px; border-bottom: 1px solid var(--border-color);">${r}</div>`).join('')
                : '<p style="color: var(--text-tertiary); text-align: center;">No results found</p>';
        });

        searchInput.focus();
    }

    clearWorkspace() {
        if (!confirm('Clear all results from workspace?')) return;
        
        document.getElementById('workspaceContent').innerHTML = `
            <div class="welcome-screen">
                <div class="welcome-icon"><i class="fas fa-chart-bar"></i></div>
                <h1>Workspace Cleared</h1>
                <p>Ask a question to see new results</p>
            </div>
        `;
        this.showNotification('Workspace cleared', 'success');
    }

    showSettings() {
        this.createModal('Settings', `
            <div style="display: flex; flex-direction: column; gap: 16px;">
                <div>
                    <label style="display: block; margin-bottom: 8px; color: var(--text-primary);">Theme</label>
                    <select id="themeSelect" style="width: 100%; padding: 8px; background: var(--bg-tertiary); 
                                                     border: 1px solid var(--border-color); border-radius: 6px; 
                                                     color: var(--text-primary);">
                        <option value="dark">Dark</option>
                        <option value="light">Light</option>
                    </select>
                </div>
                <div>
                    <label style="display: block; margin-bottom: 8px; color: var(--text-primary);">Font Size</label>
                    <select id="fontSelect" style="width: 100%; padding: 8px; background: var(--bg-tertiary); 
                                                    border: 1px solid var(--border-color); border-radius: 6px; 
                                                    color: var(--text-primary);">
                        <option value="small">Small</option>
                        <option value="medium" selected>Medium</option>
                        <option value="large">Large</option>
                    </select>
                </div>
                <div>
                    <label style="display: flex; align-items: center; gap: 8px; color: var(--text-primary); cursor: pointer;">
                        <input type="checkbox" id="autoLoadCheck" checked>
                        Auto-load dataset on startup
                    </label>
                </div>
            </div>
        `);
    }

    showHelp() {
        this.createModal('Help & Guide', `
            <div style="color: var(--text-secondary); line-height: 1.8;">
                <h3 style="color: var(--text-primary); margin-bottom: 12px;">Quick Start</h3>
                <ol style="padding-left: 20px;">
                    <li>Dataset loads automatically on startup</li>
                    <li>View columns in the left sidebar</li>
                    <li>Ask questions in the chat (right sidebar)</li>
                    <li>See results in the middle workspace</li>
                </ol>

                <h3 style="color: var(--text-primary); margin: 20px 0 12px;">Sample Questions</h3>
                <ul style="padding-left: 20px;">
                    <li>What is the average transaction amount?</li>
                    <li>Show me failure rates</li>
                    <li>How many transactions are there?</li>
                    <li>Compare P2P and P2M transactions</li>
                </ul>

                <h3 style="color: var(--text-primary); margin: 20px 0 12px;">Keyboard Shortcuts</h3>
                <ul style="padding-left: 20px;">
                    <li><kbd>Ctrl+R</kbd> - Refresh data</li>
                    <li><kbd>Ctrl+E</kbd> - Export results</li>
                    <li><kbd>Ctrl+K</kbd> - Search</li>
                    <li><kbd>Enter</kbd> - Send message</li>
                </ul>
            </div>
        `);
    }

    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        const btn = document.getElementById('themeBtn');
        const icon = btn?.querySelector('i');
        
        if (this.theme === 'light') {
            if (icon) icon.className = 'fas fa-sun';
            document.body.classList.add('light-theme');
            localStorage.setItem('theme', 'light');
        } else {
            if (icon) icon.className = 'fas fa-moon';
            document.body.classList.remove('light-theme');
            localStorage.setItem('theme', 'dark');
        }
        
        this.showNotification(`Switched to ${this.theme} theme`, 'info');
    }

    // Initialize theme from localStorage
    initTheme() {
        const savedTheme = localStorage.getItem('theme') || 'dark';
        this.theme = savedTheme;
        
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
            const btn = document.getElementById('themeBtn');
            const icon = btn?.querySelector('i');
            if (icon) icon.className = 'fas fa-sun';
        }
    }

    // Chat Actions
    clearChat() {
        if (!confirm('Clear chat history?')) return;
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="chat-message assistant">
                <div class="message-icon"><i class="fas fa-robot"></i></div>
                <div class="message-content">
                    <div class="message-text">
                        <p>Chat cleared! Ask me anything about your transaction data.</p>
                    </div>
                </div>
            </div>
        `;
        this.showNotification('Chat cleared', 'success');
    }

    saveConversation() {
        const messages = [];
        document.querySelectorAll('.chat-message').forEach(msg => {
            const isUser = msg.classList.contains('user');
            const text = msg.querySelector('.message-text')?.textContent;
            messages.push({ role: isUser ? 'user' : 'assistant', content: text });
        });

        const blob = new Blob([JSON.stringify(messages, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `conversation-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Conversation saved', 'success');
    }

    showFavorites() {
        const favQueries = [
            'What is the average transaction amount?',
            'Show me failure rates by transaction type',
            'How many P2P transactions are there?',
            'Compare Android and iOS success rates',
            'What are peak transaction hours?'
        ];

        const modal = this.createModal('Favorite Queries', `
            <div style="display: flex; flex-direction: column; gap: 8px;">
                ${favQueries.map(q => `
                    <button class="fav-query-btn" data-query="${q}" 
                            style="padding: 12px; background: var(--bg-tertiary); border: 1px solid var(--border-color); 
                                   border-radius: 6px; color: var(--text-primary); cursor: pointer; text-align: left; 
                                   transition: all 0.2s;">
                        ${q}
                    </button>
                `).join('')}
            </div>
        `);

        modal.querySelectorAll('.fav-query-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                document.getElementById('chatInput').value = query;
                this.closeModal();
                document.getElementById('sendMessage').click();
            });
            btn.addEventListener('mouseenter', (e) => {
                e.target.style.background = 'var(--bg-hover)';
                e.target.style.borderColor = 'var(--accent-blue)';
            });
            btn.addEventListener('mouseleave', (e) => {
                e.target.style.background = 'var(--bg-tertiary)';
                e.target.style.borderColor = 'var(--border-color)';
            });
        });
    }

    // Input Actions
    attachFile() {
        this.showNotification('File attachment coming soon', 'info');
    }

    voiceInput() {
        this.showNotification('Voice input coming soon', 'info');
    }

    quickStats() {
        const queries = [
            'Show me overall statistics',
            'What is the total transaction volume?',
            'How many transactions failed?',
            'What is the average amount?'
        ];

        const modal = this.createModal('Quick Statistics', `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                ${queries.map(q => `
                    <button class="quick-stat-btn" data-query="${q}"
                            style="padding: 16px; background: var(--bg-tertiary); border: 1px solid var(--border-color); 
                                   border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 13px; 
                                   transition: all 0.2s;">
                        <i class="fas fa-chart-line" style="display: block; font-size: 24px; margin-bottom: 8px;"></i>
                        ${q.replace('Show me ', '').replace('What is the ', '')}
                    </button>
                `).join('')}
            </div>
        `);

        modal.querySelectorAll('.quick-stat-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                document.getElementById('chatInput').value = query;
                this.closeModal();
                document.getElementById('sendMessage').click();
            });
        });
    }

    // Result Card Actions
    pinResult(card) {
        const cardId = card.getAttribute('data-id') || Date.now();
        card.setAttribute('data-id', cardId);

        if (this.pinnedResults.has(cardId)) {
            this.pinnedResults.delete(cardId);
            card.classList.remove('pinned');
            card.querySelector('.pin')?.classList.remove('active');
        } else {
            this.pinnedResults.add(cardId);
            card.classList.add('pinned');
            card.querySelector('.pin')?.classList.add('active');
        }
    }

    copyResult(card) {
        const text = card.querySelector('.output-body')?.textContent || '';
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard', 'success');
        });
    }

    downloadResult(card) {
        const title = card.querySelector('.output-title')?.textContent || 'result';
        const content = card.querySelector('.output-body')?.textContent || '';
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title.replace(/\s+/g, '-')}-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Result downloaded', 'success');
    }

    closeResult(card) {
        card.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => card.remove(), 300);
    }

    // Utility Functions
    createModal(title, content) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title">${title}</div>
                    <button class="modal-close"><i class="fas fa-times"></i></button>
                </div>
                <div class="modal-body">${content}</div>
            </div>
        `;

        overlay.querySelector('.modal-close').addEventListener('click', () => this.closeModal());
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) this.closeModal();
        });

        document.body.appendChild(overlay);
        return overlay;
    }

    closeModal() {
        document.querySelector('.modal-overlay')?.remove();
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-left: 3px solid var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : type === 'warning' ? 'warning' : 'info'});
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        `;
        notification.textContent = message;

        document.body.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Export for use in renderer
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IconActions;
}
