/**
 * Frontend Enhancements for Hackathon Features
 * - Query suggestions with auto-complete
 * - Statistical significance badges
 * - Methodology explainer
 * - Proactive insights display
 * - Anomaly alerts
 */

const API_URL = 'http://localhost:5000';

// Query Suggestions Auto-Complete
let suggestionsVisible = false;
let currentSuggestions = [];

function initQuerySuggestions() {
    const chatInput = document.getElementById('chatInput');
    if (!chatInput) return;
    
    // Create suggestions dropdown
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.id = 'querySuggestions';
    suggestionsDiv.className = 'query-suggestions hidden';
    chatInput.parentElement.appendChild(suggestionsDiv);
    
    // Listen for input
    let debounceTimer;
    chatInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            fetchQuerySuggestions(e.target.value);
        }, 300);
    });
    
    // Hide on blur (with delay for click)
    chatInput.addEventListener('blur', () => {
        setTimeout(() => hideSuggestions(), 200);
    });
    
    // Show example queries on focus if empty
    chatInput.addEventListener('focus', () => {
        if (!chatInput.value.trim()) {
            fetchQuerySuggestions('');
        }
    });
}

async function fetchQuerySuggestions(query) {
    try {
        const response = await fetch(`${API_URL}/query-suggestions?q=${encodeURIComponent(query)}&limit=8`);
        const data = await response.json();
        
        if (data.status === 'success') {
            currentSuggestions = data.suggestions;
            displaySuggestions(data.suggestions, data.typo_correction);
        }
    } catch (error) {
        console.error('Failed to fetch suggestions:', error);
    }
}

function displaySuggestions(suggestions, typoCorrection) {
    const suggestionsDiv = document.getElementById('querySuggestions');
    if (!suggestionsDiv) return;
    
    if (suggestions.length === 0) {
        hideSuggestions();
        return;
    }
    
    let html = '';
    
    // Show typo correction if available
    if (typoCorrection && typoCorrection.has_typo) {
        html += `
            <div class="suggestion-item typo-correction" onclick="applySuggestion('${typoCorrection.corrected}')">
                <i class="fas fa-spell-check"></i>
                <div class="suggestion-content">
                    <div class="suggestion-title">Did you mean: "${typoCorrection.corrected}"?</div>
                    <div class="suggestion-desc">Typo correction</div>
                </div>
            </div>
        `;
    }
    
    // Show suggestions
    suggestions.forEach((sug, idx) => {
        const icon = getCategoryIcon(sug.category);
        html += `
            <div class="suggestion-item" onclick="applySuggestion('${sug.query.replace(/'/g, "\\'")}')">
                <i class="fas fa-${icon}"></i>
                <div class="suggestion-content">
                    <div class="suggestion-title">${sug.query}</div>
                    <div class="suggestion-desc">${sug.description}</div>
                </div>
                <span class="suggestion-category">${sug.category}</span>
            </div>
        `;
    });
    
    suggestionsDiv.innerHTML = html;
    suggestionsDiv.classList.remove('hidden');
    suggestionsVisible = true;
}

function hideSuggestions() {
    const suggestionsDiv = document.getElementById('querySuggestions');
    if (suggestionsDiv) {
        suggestionsDiv.classList.add('hidden');
        suggestionsVisible = false;
    }
}

function applySuggestion(query) {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = query;
        chatInput.focus();
        hideSuggestions();
    }
}

function getCategoryIcon(category) {
    const icons = {
        'Overview': 'chart-pie',
        'Comparison': 'balance-scale',
        'Ranking': 'trophy',
        'Analysis': 'microscope',
        'Filtering': 'filter',
        'Trend': 'chart-line'
    };
    return icons[category] || 'question-circle';
}

// Display Statistical Insights
function displayStatisticalInsights(statistical) {
    if (!statistical) return '';
    
    let html = '<div class="statistical-insights-section">';
    
    // Data Quality Badge
    if (statistical.data_quality) {
        const dq = statistical.data_quality;
        const confidenceClass = dq.confidence.toLowerCase();
        
        html += `
            <div class="data-quality-card">
                <div class="dq-header">
                    <i class="fas fa-check-circle"></i>
                    <span>Data Quality: ${dq.adequacy}</span>
                </div>
                <div class="dq-stats">
                    <div class="dq-stat">
                        <span class="dq-label">Sample Size</span>
                        <span class="dq-value">${dq.sample_size.toLocaleString()} rows (${dq.sample_percentage}%)</span>
                    </div>
                    <div class="dq-stat">
                        <span class="dq-label">Confidence</span>
                        <span class="dq-value confidence-badge ${confidenceClass}">${dq.confidence}</span>
                    </div>
                    <div class="dq-stat">
                        <span class="dq-label">Completeness</span>
                        <span class="dq-value">${dq.completeness}%</span>
                    </div>
                </div>
                <div class="dq-recommendation">${dq.recommendation}</div>
            </div>
        `;
    }
    
    // Statistical Comparison
    if (statistical.statistical_comparison) {
        const sc = statistical.statistical_comparison;
        const sigBadge = sc.is_significant ? 
            '<span class="sig-badge significant">✓ Statistically Significant</span>' :
            '<span class="sig-badge not-significant">Not Significant</span>';
        
        html += `
            <div class="statistical-comparison-card">
                <div class="sc-header">
                    <i class="fas fa-chart-bar"></i>
                    <span>Statistical Comparison</span>
                    ${sigBadge}
                </div>
                <div class="sc-comparison">
                    <div class="sc-group">
                        <div class="sc-group-name">${sc.group1_name}</div>
                        <div class="sc-group-value">${sc.group1_value}%</div>
                    </div>
                    <div class="sc-vs">vs</div>
                    <div class="sc-group">
                        <div class="sc-group-name">${sc.group2_name}</div>
                        <div class="sc-group-value">${sc.group2_value}%</div>
                    </div>
                </div>
                <div class="sc-details">
                    <div class="sc-detail">
                        <span class="sc-label">P-Value:</span>
                        <span class="sc-value">${sc.p_value}</span>
                    </div>
                    <div class="sc-detail">
                        <span class="sc-label">Effect Size:</span>
                        <span class="sc-value">${sc.effect_size} (${sc.effect_description})</span>
                    </div>
                    <div class="sc-detail">
                        <span class="sc-label">95% CI:</span>
                        <span class="sc-value">${sc.confidence_interval.lower}% to ${sc.confidence_interval.upper}%</span>
                    </div>
                </div>
                <div class="sc-interpretation">${sc.interpretation}</div>
            </div>
        `;
    }
    
    // Anomalies
    if (statistical.anomalies && statistical.anomalies.length > 0) {
        html += '<div class="anomalies-section"><h4><i class="fas fa-exclamation-triangle"></i> Anomalies Detected</h4>';
        
        statistical.anomalies.forEach(anomaly => {
            const severityClass = anomaly.severity;
            html += `
                <div class="anomaly-card ${severityClass}">
                    <div class="anomaly-header">
                        <span class="anomaly-category">${anomaly.category}</span>
                        <span class="anomaly-severity">${anomaly.severity}</span>
                    </div>
                    <div class="anomaly-message">${anomaly.message}</div>
                    <div class="anomaly-stats">
                        <span>Value: ${anomaly.value}</span>
                        <span>Mean: ${anomaly.mean}</span>
                        <span>Z-Score: ${anomaly.z_score}</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

// Display Methodology
function displayMethodology(methodology) {
    if (!methodology) return '';
    
    let html = `
        <div class="methodology-section">
            <div class="methodology-header" onclick="toggleMethodology()">
                <i class="fas fa-cogs"></i>
                <span>Show Methodology</span>
                <i class="fas fa-chevron-down toggle-icon"></i>
            </div>
            <div class="methodology-content hidden">
                <div class="methodology-steps">
    `;
    
    methodology.steps.forEach(step => {
        html += `
            <div class="method-step">
                <div class="step-number">${step.step}</div>
                <div class="step-content">
                    <div class="step-action">
                        <i class="fas fa-${step.icon}"></i>
                        ${step.action}
                    </div>
                    <div class="step-description">${step.description}</div>
                    <div class="step-details">${step.details}</div>
                </div>
            </div>
        `;
    });
    
    html += `
                </div>
                <div class="methodology-summary">
                    <h5>Techniques Used:</h5>
                    <div class="techniques-list">
                        ${methodology.techniques_used.map(t => `<span class="technique-badge">${t}</span>`).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return html;
}

function toggleMethodology() {
    const content = document.querySelector('.methodology-content');
    const icon = document.querySelector('.methodology-header .toggle-icon');
    if (content && icon) {
        content.classList.toggle('hidden');
        icon.classList.toggle('fa-chevron-down');
        icon.classList.toggle('fa-chevron-up');
    }
}

// Display Proactive Suggestions
function displayProactiveSuggestions(proactive) {
    if (!proactive) return '';
    
    let html = '<div class="proactive-section">';
    
    // Proactive Alerts
    if (proactive.proactive_alerts && proactive.proactive_alerts.length > 0) {
        html += '<div class="proactive-alerts">';
        
        proactive.proactive_alerts.forEach(alert => {
            html += `
                <div class="proactive-alert ${alert.type}">
                    <div class="alert-icon">
                        <i class="fas fa-${alert.icon}"></i>
                    </div>
                    <div class="alert-content">
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-message">${alert.message}</div>
                        <div class="alert-action">${alert.action}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    // Follow-up Questions
    if (proactive.follow_up_questions && proactive.follow_up_questions.length > 0) {
        html += `
            <div class="follow-up-section">
                <h4><i class="fas fa-lightbulb"></i> Suggested Follow-Up Questions</h4>
                <div class="follow-up-grid">
        `;
        
        proactive.follow_up_questions.forEach(q => {
            html += `
                <div class="follow-up-card" onclick="askFollowUp('${q.replace(/'/g, "\\'")}')">
                    <i class="fas fa-arrow-right"></i>
                    <span>${q}</span>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    // Related Analyses
    if (proactive.related_analyses && proactive.related_analyses.length > 0) {
        html += `
            <div class="related-analyses-section">
                <h4><i class="fas fa-project-diagram"></i> Related Analyses</h4>
                <div class="related-grid">
        `;
        
        proactive.related_analyses.forEach(analysis => {
            html += `
                <div class="related-card" onclick="askFollowUp('${analysis.query.replace(/'/g, "\\'")}')">
                    <div class="related-icon">
                        <i class="fas fa-${analysis.icon}"></i>
                    </div>
                    <div class="related-content">
                        <div class="related-title">${analysis.title}</div>
                        <div class="related-desc">${analysis.description}</div>
                        <div class="related-benefit">${analysis.benefit}</div>
                    </div>
                </div>
            `;
        });
        
        html += '</div></div>';
    }
    
    html += '</div>';
    return html;
}

// Initialize on load
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', () => {
        initQuerySuggestions();
        console.log('[Enhancements] Query suggestions initialized');
    });
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        displayStatisticalInsights,
        displayMethodology,
        displayProactiveSuggestions,
        applySuggestion
    };
}
