/**
 * Advanced Analytics Dashboard
 * Professional KPI cards, overview charts, and interactive visualizations
 */

// Dashboard state
let dashboardData = {
    kpis: {},
    charts: [],
    lastUpdate: null
};

// Initialize dashboard on data load
async function initializeDashboard() {
    try {
        // Fetch dashboard data from backend
        const response = await axios.get(`${API_URL}/dashboard-stats`);
        
        if (response.data.status === 'success') {
            dashboardData.kpis = response.data.kpis;
            dashboardData.lastUpdate = Date.now();
            
            // Render KPI cards
            renderKPICards(dashboardData.kpis);
            
            // Render overview dashboard
            renderOverviewDashboard(response.data.overview);
            
            console.log('Dashboard initialized successfully');
        }
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        showEmptyDashboard();
    }
}

// Render KPI Cards
function renderKPICards(kpis) {
    // KPI cards disabled - user doesn't want them
    console.log('KPI cards disabled');
    return;
    
    const kpiContainer = document.getElementById('kpiCards');
    if (!kpiContainer) return;
    
    const kpiHTML = `
        <div class="kpi-card" data-kpi="total">
            <div class="kpi-icon">
                <i class="fas fa-receipt"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Total Transactions</div>
                <div class="kpi-value">${formatNumber(kpis.total_transactions)}</div>
                <div class="kpi-trend ${kpis.total_trend >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.total_trend >= 0 ? 'up' : 'down'}"></i>
                    <span>${Math.abs(kpis.total_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
        
        <div class="kpi-card success" data-kpi="success">
            <div class="kpi-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Success Rate</div>
                <div class="kpi-value">${kpis.success_rate}%</div>
                <div class="kpi-trend ${kpis.success_trend >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.success_trend >= 0 ? 'up' : 'down'}"></i>
                    <span>${Math.abs(kpis.success_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
        
        <div class="kpi-card warning" data-kpi="failure">
            <div class="kpi-icon">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Failure Rate</div>
                <div class="kpi-value">${kpis.failure_rate}%</div>
                <div class="kpi-trend ${kpis.failure_trend <= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.failure_trend <= 0 ? 'down' : 'up'}"></i>
                    <span>${Math.abs(kpis.failure_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
        
        <div class="kpi-card danger" data-kpi="fraud">
            <div class="kpi-icon">
                <i class="fas fa-shield-alt"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Fraud Flag Rate</div>
                <div class="kpi-value">${kpis.fraud_rate}%</div>
                <div class="kpi-trend ${kpis.fraud_trend <= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.fraud_trend <= 0 ? 'down' : 'up'}"></i>
                    <span>${Math.abs(kpis.fraud_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
        
        <div class="kpi-card info" data-kpi="amount">
            <div class="kpi-icon">
                <i class="fas fa-rupee-sign"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Avg Transaction</div>
                <div class="kpi-value">₹${formatNumber(kpis.avg_amount)}</div>
                <div class="kpi-trend ${kpis.amount_trend >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.amount_trend >= 0 ? 'up' : 'down'}"></i>
                    <span>${Math.abs(kpis.amount_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
        
        <div class="kpi-card primary" data-kpi="volume">
            <div class="kpi-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <div class="kpi-content">
                <div class="kpi-label">Total Volume</div>
                <div class="kpi-value">₹${formatAmount(kpis.total_volume)}</div>
                <div class="kpi-trend ${kpis.volume_trend >= 0 ? 'positive' : 'negative'}">
                    <i class="fas fa-arrow-${kpis.volume_trend >= 0 ? 'up' : 'down'}"></i>
                    <span>${Math.abs(kpis.volume_trend || 0)}% vs yesterday</span>
                </div>
            </div>
        </div>
    `;
    
    kpiContainer.innerHTML = kpiHTML;
    
    // Add click handlers for drill-down
    kpiContainer.querySelectorAll('.kpi-card').forEach(card => {
        card.addEventListener('click', () => {
            const kpiType = card.dataset.kpi;
            handleKPIDrillDown(kpiType);
        });
    });
    
    // Animate cards
    animateKPICards();
}

// Render Overview Dashboard
function renderOverviewDashboard(overviewData) {
    const container = document.getElementById('dashboardCharts');
    if (!container) return;
    
    container.innerHTML = `
        <div class="dashboard-header">
            <h2 class="dashboard-title">
                <i class="fas fa-chart-pie"></i>
                Overview Dashboard
            </h2>
            <div class="dashboard-actions">
                <button class="dashboard-btn" onclick="refreshDashboard()">
                    <i class="fas fa-sync-alt"></i>
                    Refresh
                </button>
                <button class="dashboard-btn" onclick="exportDashboard()">
                    <i class="fas fa-download"></i>
                    Export
                </button>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-chart-card" id="chart-transaction-trend">
                <div class="chart-card-header">
                    <h3>Transaction Volume Trend</h3>
                    <span class="chart-subtitle">Last 7 days</span>
                </div>
                <div class="chart-card-body">
                    <div id="trendChart" class="dashboard-chart"></div>
                </div>
            </div>
            
            <div class="dashboard-chart-card" id="chart-bank-distribution">
                <div class="chart-card-header">
                    <h3>Top Banks by Volume</h3>
                    <span class="chart-subtitle">Transaction count</span>
                </div>
                <div class="chart-card-body">
                    <div id="bankChart" class="dashboard-chart"></div>
                </div>
            </div>
            
            <div class="dashboard-chart-card" id="chart-type-distribution">
                <div class="chart-card-header">
                    <h3>Transaction Type Distribution</h3>
                    <span class="chart-subtitle">By category</span>
                </div>
                <div class="chart-card-body">
                    <div id="typeChart" class="dashboard-chart"></div>
                </div>
            </div>
            
            <div class="dashboard-chart-card" id="chart-hourly-pattern">
                <div class="chart-card-header">
                    <h3>Hourly Transaction Pattern</h3>
                    <span class="chart-subtitle">24-hour view</span>
                </div>
                <div class="chart-card-body">
                    <div id="hourlyChart" class="dashboard-chart"></div>
                </div>
            </div>
        </div>
    `;
    
    // Render individual charts
    renderTrendChart(overviewData.trend);
    renderBankChart(overviewData.banks);
    renderTypeChart(overviewData.types);
    renderHourlyChart(overviewData.hourly);
}

// Render Trend Chart
function renderTrendChart(data) {
    const chart = echarts.init(document.getElementById('trendChart'), 'dark');
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: {
            type: 'category',
            data: data.dates,
            axisLabel: { color: '#858585' },
            axisLine: { lineStyle: { color: '#3e3e42' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#858585' },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        },
        series: [{
            name: 'Transactions',
            type: 'line',
            data: data.values,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(0, 122, 204, 0.4)' },
                    { offset: 1, color: 'rgba(0, 122, 204, 0.05)' }
                ])
            },
            itemStyle: { color: '#007acc' },
            lineStyle: { width: 3 }
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    
    // Store chart instance
    window.dashboardCharts = window.dashboardCharts || {};
    window.dashboardCharts.trend = chart;
}

// Render Bank Chart
function renderBankChart(data) {
    const chart = echarts.init(document.getElementById('bankChart'), 'dark');
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: {
            type: 'value',
            axisLabel: { color: '#858585' },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        },
        yAxis: {
            type: 'category',
            data: data.banks,
            axisLabel: { color: '#858585' }
        },
        series: [{
            name: 'Transactions',
            type: 'bar',
            data: data.values,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                    { offset: 0, color: '#007acc' },
                    { offset: 1, color: '#1e8ad6' }
                ]),
                borderRadius: [0, 4, 4, 0]
            },
            label: {
                show: true,
                position: 'right',
                formatter: '{c}',
                color: '#cccccc'
            }
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    
    // Add click handler for drill-down
    chart.on('click', (params) => {
        const bank = params.name;
        drillDownToBank(bank);
    });
    
    window.dashboardCharts = window.dashboardCharts || {};
    window.dashboardCharts.bank = chart;
}

// Render Type Chart
function renderTypeChart(data) {
    const chart = echarts.init(document.getElementById('typeChart'), 'dark');
    
    const pieData = data.types.map((type, index) => ({
        name: type,
        value: data.values[index],
        itemStyle: {
            color: ['#007acc', '#00c853', '#ff6b6b', '#ffd93d'][index % 4]
        }
    }));
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} ({d}%)',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            top: 'middle',
            textStyle: { color: '#858585' }
        },
        series: [{
            name: 'Transaction Type',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['60%', '50%'],
            data: pieData,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            },
            label: {
                formatter: '{b}\n{d}%',
                color: '#cccccc'
            }
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    
    window.dashboardCharts = window.dashboardCharts || {};
    window.dashboardCharts.type = chart;
}

// Render Hourly Chart
function renderHourlyChart(data) {
    const chart = echarts.init(document.getElementById('hourlyChart'), 'dark');
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1
        },
        grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
        xAxis: {
            type: 'category',
            data: data.hours,
            axisLabel: { color: '#858585' },
            axisLine: { lineStyle: { color: '#3e3e42' } }
        },
        yAxis: {
            type: 'value',
            axisLabel: { color: '#858585' },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        },
        series: [{
            name: 'Transactions',
            type: 'bar',
            data: data.values,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#007acc' },
                    { offset: 1, color: '#1e8ad6' }
                ]),
                borderRadius: [4, 4, 0, 0]
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 122, 204, 0.5)'
                }
            }
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
    
    window.dashboardCharts = window.dashboardCharts || {};
    window.dashboardCharts.hourly = chart;
}

// Handle KPI Drill-Down
function handleKPIDrillDown(kpiType) {
    const queries = {
        total: "Show me transaction volume breakdown by type",
        success: "Show me successful transactions by bank",
        failure: "Show me failed transactions by bank",
        fraud: "Show me fraud flagged transactions by merchant category",
        amount: "Show me average transaction amount by transaction type",
        volume: "Show me total transaction volume by state"
    };
    
    const query = queries[kpiType];
    if (query) {
        chatInput.value = query;
        sendQuery(query);
    }
}

// Drill down to specific bank
function drillDownToBank(bank) {
    const query = `Show me detailed analysis for ${bank} bank`;
    chatInput.value = query;
    sendQuery(query);
}

// Animate KPI Cards
function animateKPICards() {
    const cards = document.querySelectorAll('.kpi-card');
    cards.forEach((card, index) => {
        card.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s both`;
    });
}

// Refresh Dashboard
function refreshDashboard() {
    showNotification('Refreshing dashboard...', 'info');
    initializeDashboard();
}

// Export Dashboard
function exportDashboard() {
    showNotification('Exporting dashboard...', 'info');
    
    // Export all charts as images
    const charts = window.dashboardCharts || {};
    Object.keys(charts).forEach(key => {
        const chart = charts[key];
        const url = chart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#1e1e1e'
        });
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `dashboard-${key}-${Date.now()}.png`;
        link.click();
    });
    
    showNotification('Dashboard exported successfully', 'success');
}

// Show Empty Dashboard
function showEmptyDashboard() {
    const container = document.getElementById('dashboardCharts');
    if (!container) return;
    
    container.innerHTML = `
        <div class="empty-dashboard">
            <div class="empty-icon">
                <i class="fas fa-chart-line"></i>
            </div>
            <h3>Welcome to InsightX Analytics</h3>
            <p>Load your dataset to see the overview dashboard</p>
            <div class="suggested-queries">
                <h4>Try asking:</h4>
                <button class="suggested-query-btn" onclick="askSuggested('Which bank has the highest failure rate?')">
                    Which bank has the highest failure rate?
                </button>
                <button class="suggested-query-btn" onclick="askSuggested('Show me transaction trends by hour')">
                    Show me transaction trends by hour
                </button>
                <button class="suggested-query-btn" onclick="askSuggested('What is the fraud rate by merchant category?')">
                    What is the fraud rate by merchant category?
                </button>
            </div>
        </div>
    `;
}

// Ask suggested query
function askSuggested(query) {
    chatInput.value = query;
    sendQuery(query);
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toLocaleString();
}

function formatAmount(num) {
    if (num >= 10000000) return (num / 10000000).toFixed(2) + ' Cr';
    if (num >= 100000) return (num / 100000).toFixed(2) + ' L';
    if (num >= 1000) return (num / 1000).toFixed(2) + ' K';
    return num.toLocaleString();
}

// Make functions globally available
window.initializeDashboard = initializeDashboard;
window.refreshDashboard = refreshDashboard;
window.exportDashboard = exportDashboard;
window.handleKPIDrillDown = handleKPIDrillDown;
window.drillDownToBank = drillDownToBank;
window.askSuggested = askSuggested;
