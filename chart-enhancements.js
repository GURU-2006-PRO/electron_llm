/**
 * Enhanced ECharts Visualization System
 * Inline chart generation prompt (Cursor IDE style)
 */

// Chart configuration presets
const CHART_PRESETS = {
    bar: {
        colors: ['#007acc', '#1e8ad6', '#4a9eff', '#6bb3ff'],
        gradient: true
    },
    line: {
        colors: ['#007acc', '#00c853', '#ff6b6b', '#ffd93d'],
        smooth: true
    },
    pie: {
        colors: ['#007acc', '#00c853', '#ff6b6b', '#ffd93d', '#a78bfa', '#fb923c'],
        radius: ['40%', '70%']
    }
};

// Show inline chart generation prompt (Cursor IDE style)
function showChartGenerationPrompt(data, suggestedChartType, query) {
    const promptDiv = document.createElement('div');
    promptDiv.className = 'chat-message assistant chart-prompt';
    promptDiv.innerHTML = `
        <div class="message-icon">
            <i class="fas fa-chart-bar"></i>
        </div>
        <div class="message-content">
            <div class="chart-prompt-content">
                <div class="chart-prompt-text">
                    <i class="fas fa-info-circle"></i>
                    <span>I found <strong>${data.length} data points</strong> that can be visualized. Would you like me to generate a chart?</span>
                </div>
                <div class="chart-prompt-actions">
                    <button class="chart-prompt-btn secondary" onclick="skipChartGeneration(this)">
                        <i class="fas fa-times"></i>
                        Skip
                    </button>
                    <button class="chart-prompt-btn primary" onclick="confirmChartGeneration(this, '${suggestedChartType}', '${query}')">
                        <i class="fas fa-chart-line"></i>
                        Generate Chart
                    </button>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(promptDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Store data for later use
    promptDiv.dataset.chartData = JSON.stringify(data);
    promptDiv.dataset.chartType = suggestedChartType;
    promptDiv.dataset.query = query;
    
    return promptDiv;
}

// Skip chart generation
function skipChartGeneration(button) {
    const promptDiv = button.closest('.chart-prompt');
    promptDiv.classList.add('chart-prompt-dismissed');
    
    // Update message to show it was skipped
    const content = promptDiv.querySelector('.chart-prompt-content');
    content.innerHTML = `
        <div class="chart-prompt-result skipped">
            <i class="fas fa-times-circle"></i>
            <span>Chart generation skipped</span>
        </div>
    `;
}

// Confirm chart generation
function confirmChartGeneration(button, chartType, query) {
    const promptDiv = button.closest('.chart-prompt');
    const data = JSON.parse(promptDiv.dataset.chartData);
    
    // Update message to show it's generating
    const content = promptDiv.querySelector('.chart-prompt-content');
    content.innerHTML = `
        <div class="chart-prompt-result generating">
            <div class="spinner-small"></div>
            <span>Generating chart...</span>
        </div>
    `;
    
    // Generate chart after brief delay for UX
    setTimeout(() => {
        renderEnhancedChart(data, chartType, {
            title: query,
            seriesName: 'Analysis'
        });
        
        // Update to success state
        content.innerHTML = `
            <div class="chart-prompt-result success">
                <i class="fas fa-check-circle"></i>
                <span>Chart generated successfully</span>
            </div>
        `;
        
        promptDiv.classList.add('chart-prompt-completed');
    }, 300);
}

// Enhanced chart rendering
function renderEnhancedChart(data, chartType, chartConfig) {
    console.log('[renderEnhancedChart] ========== START ==========');
    console.log('[renderEnhancedChart] Data:', data);
    console.log('[renderEnhancedChart] Chart type:', chartType);
    console.log('[renderEnhancedChart] Config:', chartConfig);
    
    if (!data || data.length === 0) {
        console.error('[renderEnhancedChart] No data provided');
        return;
    }
    
    try {
        // Verify workspaceContent exists
        if (typeof workspaceContent === 'undefined' || !workspaceContent) {
            throw new Error('workspaceContent element not found');
        }
        console.log('[renderEnhancedChart] workspaceContent found');
        
        const chartCard = document.createElement('div');
        chartCard.className = 'output-card chart-card enhanced-chart';
        const chartId = 'chart-' + Date.now();
        
        chartCard.innerHTML = `
            <div class="output-header">
                <div class="output-title">
                    <i class="fas fa-chart-${chartType === 'donut' ? 'pie' : chartType === 'vertical_bar' ? 'bar' : 'line'}"></i>
                    ${chartConfig?.title || 'Data Visualization'}
                </div>
                <div class="chart-actions">
                    <button class="chart-action-btn" onclick="downloadChart('${chartId}')" title="Download as PNG">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="chart-action-btn" onclick="fullscreenChart('${chartId}')" title="Fullscreen">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            <div class="output-body">
                <div id="${chartId}" class="echart-container enhanced"></div>
            </div>
        `;
        
        console.log('[renderEnhancedChart] Chart card created with ID:', chartId);
        
        workspaceContent.insertBefore(chartCard, workspaceContent.firstChild);
        console.log('[renderEnhancedChart] Chart card inserted into DOM');
        
        // Initialize ECharts
        const chartDom = document.getElementById(chartId);
        if (!chartDom) {
            throw new Error('Chart DOM element not found after insertion');
        }
        console.log('[renderEnhancedChart] Chart DOM element found');
        
        // Verify echarts is available
        if (typeof echarts === 'undefined') {
            throw new Error('ECharts library not loaded');
        }
        
        const myChart = echarts.init(chartDom, 'dark');
        console.log('[renderEnhancedChart] ECharts instance initialized');
        
        // Build chart options
        const option = buildEnhancedChartOption(data, chartType, chartConfig);
        console.log('[renderEnhancedChart] Chart options built:', option);
        
        myChart.setOption(option, true);
        console.log('[renderEnhancedChart] Chart options set');
        
        // Make responsive
        window.addEventListener('resize', () => myChart.resize());
        
        // Store for actions
        window.chartRegistry = window.chartRegistry || {};
        window.chartRegistry[chartId] = myChart;
        
        console.log('[renderEnhancedChart] ========== COMPLETE ==========');
        return chartId;
    } catch (error) {
        console.error('[renderEnhancedChart] ERROR:', error);
        console.error('[renderEnhancedChart] Stack:', error.stack);
        throw error;
    }
}

// Build enhanced chart options
function buildEnhancedChartOption(data, chartType, chartConfig) {
    const preset = CHART_PRESETS[chartType.replace('vertical_', '').replace('horizontal_', '')] || CHART_PRESETS.bar;
    
    const baseOption = {
        backgroundColor: 'transparent',
        animation: true,
        animationDuration: 1000,
        animationEasing: 'cubicOut',
        tooltip: {
            trigger: chartType.includes('bar') || chartType === 'line' ? 'axis' : 'item',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1,
            textStyle: { color: '#ffffff' },
            axisPointer: {
                type: chartType.includes('bar') ? 'shadow' : 'line',
                shadowStyle: { color: 'rgba(0, 122, 204, 0.1)' }
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '12%',
            containLabel: true
        }
    };
    
    if (chartType === 'vertical_bar' || chartType === 'horizontal_bar') {
        return buildBarChartOption(data, chartType, chartConfig, baseOption, preset);
    } else if (chartType === 'line' || chartType === 'area') {
        return buildLineChartOption(data, chartType, chartConfig, baseOption, preset);
    } else if (chartType === 'donut' || chartType === 'pie') {
        return buildPieChartOption(data, chartType, chartConfig, baseOption, preset);
    }
    
    return baseOption;
}

// Build bar chart
function buildBarChartOption(data, chartType, chartConfig, baseOption, preset) {
    const categories = data.map(row => String(row[Object.keys(row)[0]]));
    const values = data.map(row => {
        for (let key in row) {
            if (typeof row[key] === 'number') return row[key];
        }
        return 0;
    });
    
    // Helper function to truncate long labels
    const truncateLabel = (label, maxLength = 15) => {
        if (label.length <= maxLength) return label;
        return label.substring(0, maxLength - 3) + '...';
    };
    
    // Determine if labels need rotation based on length and count
    const maxLabelLength = Math.max(...categories.map(cat => cat.length));
    const hasLongLabels = maxLabelLength > 10;
    const hasManyCategories = categories.length > 8;
    
    // Smart rotation: only rotate if really needed
    let rotationAngle = 0;
    let gridBottom = '10%';
    let labelMaxLength = 15;
    
    if (chartType === 'vertical_bar') {
        if (hasLongLabels && hasManyCategories) {
            rotationAngle = 45;
            gridBottom = '20%';
            labelMaxLength = 20;
        } else if (hasLongLabels) {
            rotationAngle = 30;
            gridBottom = '15%';
            labelMaxLength = 18;
        } else if (hasManyCategories) {
            rotationAngle = 0;
            gridBottom = '12%';
            labelMaxLength = 12;
        }
    }
    
    return {
        ...baseOption,
        grid: {
            left: chartType === 'horizontal_bar' ? '15%' : '3%',
            right: '4%',
            bottom: gridBottom,
            top: '12%',
            containLabel: true
        },
        title: {
            text: chartConfig?.title || 'Bar Chart',
            left: 'center',
            top: '2%',
            textStyle: { color: '#cccccc', fontSize: 15, fontWeight: 600 }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1,
            textStyle: { color: '#ffffff', fontSize: 13 },
            axisPointer: {
                type: 'shadow',
                shadowStyle: { color: 'rgba(0, 122, 204, 0.1)' }
            },
            formatter: function(params) {
                const param = params[0];
                const fullLabel = categories[param.dataIndex];
                return `<strong>${fullLabel}</strong><br/>` +
                       `${param.seriesName}: ${param.value.toLocaleString()}`;
            }
        },
        xAxis: chartType === 'horizontal_bar' ? {
            type: 'value',
            axisLabel: { 
                color: '#858585',
                formatter: (value) => value.toLocaleString(),
                fontSize: 11
            },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        } : {
            type: 'category',
            data: categories,
            axisLabel: { 
                color: '#858585', 
                rotate: rotationAngle,
                interval: 0,
                formatter: (value) => truncateLabel(value, labelMaxLength),
                fontSize: 11,
                margin: 10
            },
            axisLine: { lineStyle: { color: '#3e3e42' } },
            axisTick: { alignWithLabel: true }
        },
        yAxis: chartType === 'horizontal_bar' ? {
            type: 'category',
            data: categories,
            axisLabel: { 
                color: '#858585',
                formatter: (value) => truncateLabel(value, 25),
                fontSize: 11
            },
            axisLine: { lineStyle: { color: '#3e3e42' } }
        } : {
            type: 'value',
            axisLabel: { 
                color: '#858585',
                formatter: (value) => value.toLocaleString(),
                fontSize: 11
            },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        },
        series: [{
            name: chartConfig?.seriesName || 'Value',
            type: 'bar',
            data: values,
            barMaxWidth: 60,
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: preset.colors[0] },
                    { offset: 1, color: preset.colors[1] }
                ]),
                borderRadius: chartType === 'horizontal_bar' ? [0, 4, 4, 0] : [4, 4, 0, 0]
            },
            label: {
                show: values.length <= 15,
                position: chartType === 'horizontal_bar' ? 'right' : 'top',
                formatter: (params) => params.value.toLocaleString(),
                color: '#cccccc',
                fontSize: 10
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 122, 204, 0.5)'
                }
            }
        }]
    };
}

// Build line chart
function buildLineChartOption(data, chartType, chartConfig, baseOption, preset) {
    const categories = data.map(row => String(row[Object.keys(row)[0]]));
    const values = data.map(row => {
        for (let key in row) {
            if (typeof row[key] === 'number') return row[key];
        }
        return 0;
    });
    
    // Helper function to truncate long labels
    const truncateLabel = (label, maxLength = 12) => {
        if (label.length <= maxLength) return label;
        return label.substring(0, maxLength - 3) + '...';
    };
    
    // Determine if labels need rotation
    const hasLongLabels = categories.some(cat => cat.length > 12);
    const hasManyCategories = categories.length > 10;
    const shouldRotate = hasLongLabels || hasManyCategories;
    const rotationAngle = shouldRotate ? 30 : 0;
    const gridBottom = shouldRotate ? '15%' : '10%';
    
    return {
        ...baseOption,
        grid: {
            left: '3%',
            right: '4%',
            bottom: gridBottom,
            top: '12%',
            containLabel: true
        },
        title: {
            text: chartConfig?.title || 'Trend Analysis',
            left: 'center',
            top: '2%',
            textStyle: { color: '#cccccc', fontSize: 15, fontWeight: 600 }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1,
            textStyle: { color: '#ffffff', fontSize: 13 },
            axisPointer: {
                type: 'line',
                lineStyle: { color: '#007acc', width: 1, type: 'dashed' }
            },
            formatter: function(params) {
                const param = params[0];
                const fullLabel = categories[param.dataIndex];
                return `<strong>${fullLabel}</strong><br/>` +
                       `${param.seriesName}: ${param.value.toLocaleString()}`;
            }
        },
        xAxis: {
            type: 'category',
            data: categories,
            axisLabel: { 
                color: '#858585',
                rotate: rotationAngle,
                interval: 0,
                formatter: (value) => truncateLabel(value, 12),
                fontSize: 10
            },
            axisLine: { lineStyle: { color: '#3e3e42' } },
            axisTick: { alignWithLabel: true }
        },
        yAxis: {
            type: 'value',
            axisLabel: { 
                color: '#858585',
                formatter: (value) => value.toLocaleString()
            },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        },
        series: [{
            name: chartConfig?.seriesName || 'Value',
            type: 'line',
            data: values,
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            areaStyle: chartType === 'area' ? {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(0, 122, 204, 0.4)' },
                    { offset: 1, color: 'rgba(0, 122, 204, 0.05)' }
                ])
            } : null,
            itemStyle: { color: preset.colors[0] },
            lineStyle: { width: 3 }
        }]
    };
}

// Build pie/donut chart
function buildPieChartOption(data, chartType, chartConfig, baseOption, preset) {
    console.log('[PIE CHART] Input data:', data);
    
    const pieData = data.map((row, index) => {
        console.log('[PIE CHART] Processing row:', row);
        
        // Find the name column (first non-numeric column or first column)
        let name = '';
        let value = 0;
        
        const keys = Object.keys(row);
        
        // Strategy 1: Find first string column for name
        for (let key of keys) {
            if (typeof row[key] === 'string' && row[key].length > 0) {
                name = row[key];
                break;
            }
        }
        
        // Strategy 2: If no string found, use first column
        if (!name && keys.length > 0) {
            name = String(row[keys[0]]);
        }
        
        // Find the numeric value (prefer columns with 'count', 'total', 'amount', 'value')
        const valueKeys = keys.filter(k => typeof row[k] === 'number');
        
        if (valueKeys.length > 0) {
            // Prefer specific column names
            const preferredKey = valueKeys.find(k => 
                k.toLowerCase().includes('count') || 
                k.toLowerCase().includes('total') ||
                k.toLowerCase().includes('amount') ||
                k.toLowerCase().includes('value')
            );
            
            value = preferredKey ? row[preferredKey] : row[valueKeys[0]];
        }
        
        console.log('[PIE CHART] Extracted - name:', name, 'value:', value);
        
        return {
            name: name,
            value: value,
            itemStyle: { color: preset.colors[index % preset.colors.length] }
        };
    });
    
    console.log('[PIE CHART] Final pieData:', pieData);
    
    // Calculate total for percentage display
    const total = pieData.reduce((sum, item) => sum + item.value, 0);
    
    // Determine radius based on chart type
    const radius = chartType === 'donut' ? ['40%', '70%'] : ['0%', '70%'];
    
    return {
        ...baseOption,
        title: {
            text: chartConfig?.title || 'Distribution',
            left: 'center',
            top: '2%',
            textStyle: { color: '#cccccc', fontSize: 15, fontWeight: 600 }
        },
        legend: {
            orient: 'vertical',
            left: 'left',
            top: 'middle',
            textStyle: { color: '#858585', fontSize: 11 },
            formatter: function(name) {
                // Find the data item
                const item = pieData.find(d => d.name === name);
                if (item) {
                    const percentage = ((item.value / total) * 100).toFixed(1);
                    // Truncate long names
                    const displayName = name.length > 15 ? name.substring(0, 12) + '...' : name;
                    return `${displayName} (${percentage}%)`;
                }
                return name;
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(50, 50, 50, 0.95)',
            borderColor: '#007acc',
            borderWidth: 1,
            textStyle: { color: '#ffffff', fontSize: 13 },
            formatter: function(params) {
                return `<strong>${params.name}</strong><br/>` +
                       `Value: ${params.value.toLocaleString()}<br/>` +
                       `Percentage: ${params.percent}%`;
            }
        },
        series: [{
            name: chartConfig?.seriesName || 'Distribution',
            type: 'pie',
            radius: radius,
            center: ['60%', '50%'],
            data: pieData,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                },
                label: {
                    show: true,
                    fontSize: 14,
                    fontWeight: 'bold'
                }
            },
            label: {
                formatter: function(params) {
                    // Show name and percentage on the chart
                    const name = params.name.length > 12 ? params.name.substring(0, 10) + '..' : params.name;
                    return `${name}\n${params.percent}%`;
                },
                color: '#cccccc',
                fontSize: 10,
                lineHeight: 14
            },
            labelLine: {
                lineStyle: {
                    color: '#858585'
                },
                length: 15,
                length2: 10
            }
        }]
    };
}

// Download chart
function downloadChart(chartId) {
    const chart = window.chartRegistry[chartId];
    if (!chart) return;
    
    const url = chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#1e1e1e'
    });
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `chart-${Date.now()}.png`;
    link.click();
    
    showNotification('Chart downloaded successfully', 'success');
}

// Fullscreen chart
function fullscreenChart(chartId) {
    const chartContainer = document.getElementById(chartId);
    if (!chartContainer) {
        console.error('Chart container not found:', chartId);
        return;
    }
    
    const chart = window.chartRegistry[chartId];
    if (!chart) {
        console.error('Chart instance not found:', chartId);
        return;
    }
    
    // Check if already in fullscreen
    if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement) {
        // Exit fullscreen
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        return;
    }
    
    // Enter fullscreen
    const requestFullscreen = chartContainer.requestFullscreen || 
                             chartContainer.webkitRequestFullscreen || 
                             chartContainer.mozRequestFullScreen || 
                             chartContainer.msRequestFullscreen;
    
    if (requestFullscreen) {
        requestFullscreen.call(chartContainer).then(() => {
            console.log('Entered fullscreen mode');
            // Resize chart to fit fullscreen
            setTimeout(() => {
                chart.resize();
            }, 100);
        }).catch(err => {
            console.error('Error entering fullscreen:', err);
            showNotification('Fullscreen not supported', 'error');
        });
    } else {
        console.error('Fullscreen API not supported');
        showNotification('Fullscreen not supported in this browser', 'error');
    }
}

// Listen for fullscreen changes to resize chart
document.addEventListener('fullscreenchange', handleFullscreenChange);
document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
document.addEventListener('mozfullscreenchange', handleFullscreenChange);
document.addEventListener('MSFullscreenChange', handleFullscreenChange);

function handleFullscreenChange() {
    const fullscreenElement = document.fullscreenElement || 
                             document.webkitFullscreenElement || 
                             document.mozFullScreenElement || 
                             document.msFullscreenElement;
    
    if (fullscreenElement) {
        // Entered fullscreen - resize the chart
        const chartId = fullscreenElement.id;
        const chart = window.chartRegistry[chartId];
        if (chart) {
            setTimeout(() => {
                chart.resize();
                console.log('Chart resized for fullscreen');
            }, 100);
        }
    } else {
        // Exited fullscreen - resize all charts
        Object.keys(window.chartRegistry || {}).forEach(chartId => {
            const chart = window.chartRegistry[chartId];
            if (chart) {
                setTimeout(() => {
                    chart.resize();
                    console.log('Chart resized after exiting fullscreen');
                }, 100);
            }
        });
    }
}

// Helper function for notifications (if not already defined)
function showNotification(message, type = 'info') {
    // Check if notification function exists in renderer
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
        return;
    }
    
    // Fallback notification
    const toast = document.createElement('div');
    toast.className = `toast-notification ${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : type === 'success' ? '#28a745' : '#007acc'};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make functions globally available
window.showChartGenerationPrompt = showChartGenerationPrompt;
window.skipChartGeneration = skipChartGeneration;
window.confirmChartGeneration = confirmChartGeneration;
window.renderEnhancedChart = renderEnhancedChart;
window.downloadChart = downloadChart;
window.fullscreenChart = fullscreenChart;
