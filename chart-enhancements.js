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
    if (!data || data.length === 0) return;
    
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
    
    workspaceContent.insertBefore(chartCard, workspaceContent.firstChild);
    
    // Initialize ECharts
    const chartDom = document.getElementById(chartId);
    const myChart = echarts.init(chartDom, 'dark');
    
    // Build chart options
    const option = buildEnhancedChartOption(data, chartType, chartConfig);
    myChart.setOption(option, true);
    
    // Make responsive
    window.addEventListener('resize', () => myChart.resize());
    
    // Store for actions
    window.chartRegistry = window.chartRegistry || {};
    window.chartRegistry[chartId] = myChart;
    
    return chartId;
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
        return buildPieChartOption(data, chartConfig, baseOption, preset);
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
    const truncateLabel = (label, maxLength = 12) => {
        if (label.length <= maxLength) return label;
        return label.substring(0, maxLength - 3) + '...';
    };
    
    // Determine if labels need rotation based on length and count
    const hasLongLabels = categories.some(cat => cat.length > 12);
    const hasManyCategories = categories.length > 6;
    const shouldRotate = hasLongLabels || hasManyCategories;
    const rotationAngle = hasLongLabels ? 45 : (hasManyCategories ? 30 : 0);
    
    // Adjust grid to accommodate rotated labels
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
            textStyle: { color: '#ffffff' },
            axisPointer: {
                type: 'shadow',
                shadowStyle: { color: 'rgba(0, 122, 204, 0.1)' }
            },
            formatter: function(params) {
                const param = params[0];
                const fullLabel = categories[param.dataIndex];
                return `<strong>${fullLabel}</strong><br/>${param.seriesName}: ${param.value.toLocaleString()}`;
            }
        },
        xAxis: chartType === 'horizontal_bar' ? {
            type: 'value',
            axisLabel: { 
                color: '#858585',
                formatter: (value) => value.toLocaleString()
            },
            splitLine: { lineStyle: { color: '#3e3e42' } }
        } : {
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
        yAxis: chartType === 'horizontal_bar' ? {
            type: 'category',
            data: categories,
            axisLabel: { 
                color: '#858585',
                formatter: (value) => truncateLabel(value, 20)
            }
        } : {
            type: 'value',
            axisLabel: { 
                color: '#858585',
                formatter: (value) => value.toLocaleString()
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
                borderRadius: [4, 4, 0, 0]
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
            textStyle: { color: '#ffffff' },
            axisPointer: {
                type: 'line',
                lineStyle: { color: '#007acc', width: 1, type: 'dashed' }
            },
            formatter: function(params) {
                const param = params[0];
                const fullLabel = categories[param.dataIndex];
                return `<strong>${fullLabel}</strong><br/>${param.seriesName}: ${param.value.toLocaleString()}`;
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

// Build pie chart
function buildPieChartOption(data, chartConfig, baseOption, preset) {
    const pieData = data.map((row, index) => ({
        name: String(row[Object.keys(row)[0]]),
        value: (() => {
            for (let key in row) {
                if (typeof row[key] === 'number') return row[key];
            }
            return 0;
        })(),
        itemStyle: { color: preset.colors[index % preset.colors.length] }
    }));
    
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
            textStyle: { color: '#858585', fontSize: 12 }
        },
        series: [{
            name: chartConfig?.seriesName || 'Distribution',
            type: 'pie',
            radius: preset.radius,
            center: ['60%', '50%'],
            data: pieData,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            },
            label: {
                formatter: '{b}: {d}%',
                color: '#cccccc'
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
    if (!chartContainer) return;
    
    if (chartContainer.requestFullscreen) {
        chartContainer.requestFullscreen();
    }
}

// Make functions globally available
window.showChartGenerationPrompt = showChartGenerationPrompt;
window.skipChartGeneration = skipChartGeneration;
window.confirmChartGeneration = confirmChartGeneration;
window.renderEnhancedChart = renderEnhancedChart;
window.downloadChart = downloadChart;
window.fullscreenChart = fullscreenChart;
