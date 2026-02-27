/**
 * India Map Visualization using ECharts
 * Automatically renders when state-based queries are detected
 */

// India GeoJSON coordinates (simplified for performance)
const INDIA_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        // This would contain actual GeoJSON data for India states
        // For now, we'll use ECharts' built-in map if available
        // Or use a simple representation
    ]
};

/**
 * Render India map with state-wise data
 * @param {Object} mapData - Map configuration from backend
 * @param {string} containerId - DOM element ID to render map
 */
function renderIndiaMap(mapData, containerId = null) {
    if (!mapData || mapData.type !== 'india_map') {
        console.log('[MAP] No valid map data to render');
        return;
    }

    console.log('[MAP] Rendering India map with data:', mapData);

    // Create container if not provided
    let chartContainer;
    if (containerId) {
        chartContainer = document.getElementById(containerId);
    } else {
        // Create new card in workspace
        const card = document.createElement('div');
        card.className = 'output-card map-card';
        const mapId = 'india-map-' + Date.now();
        card.innerHTML = `
            <div class="output-header">
                <div class="output-title">
                    <i class="fas fa-map-marked-alt"></i>
                    India Map - ${mapData.metric_label}
                </div>
                <div class="map-actions">
                    <button class="map-action-btn" onclick="downloadMap('${mapId}')" title="Download">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="map-action-btn" onclick="toggleMapFullscreen('${mapId}')" title="Fullscreen">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            <div class="output-body">
                <div id="${mapId}" class="india-map-container"></div>
            </div>
        `;
        
        workspaceContent.insertBefore(card, workspaceContent.firstChild);
        chartContainer = document.getElementById(mapId);
    }

    // Initialize ECharts
    const chart = echarts.init(chartContainer, 'dark');
    
    // Store chart instance
    chartContainer.chartInstance = chart;

    // Prepare data - create a map of state names to values
    const dataMap = {};
    mapData.data.forEach(item => {
        dataMap[item.name] = item.value;
    });

    // Create series data with all states
    const seriesData = mapData.data.map(item => ({
        name: item.name,
        value: item.value,
        itemStyle: {
            areaColor: getColorForValue(item.value, mapData.min_value, mapData.max_value, mapData.color_scale)
        }
    }));

    console.log('[MAP] Series data prepared:', seriesData.length, 'states');

    // ECharts configuration
    const option = {
        title: {
            text: `${mapData.metric_label} by State`,
            left: 'center',
            top: 20,
            textStyle: {
                color: '#cccccc',
                fontSize: 18,
                fontWeight: 600
            }
        },
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(30, 30, 30, 0.95)',
            borderColor: '#3e3e42',
            borderWidth: 1,
            textStyle: {
                color: '#cccccc',
                fontSize: 13
            },
            formatter: function(params) {
                if (!params.data) return params.name;
                
                const stateData = mapData.data.find(d => d.name === params.name);
                if (!stateData) return params.name;
                
                const rawData = stateData.raw_data;
                let html = `<div style="padding: 8px;">
                    <strong>${params.name}</strong><br/>
                    <hr style="margin: 8px 0; border-color: rgba(255,255,255,0.2);">`;
                
                html += `<div style="margin: 4px 0;">
                    <span style="color: #4ec9b0;">●</span> 
                    ${mapData.metric_label}: <strong>${formatValue(params.value, mapData.unit)}</strong>
                </div>`;
                
                if (rawData && rawData.total_count) {
                    html += `<div style="margin: 4px 0;">
                        <span style="color: #569cd6;">●</span> 
                        Transactions: <strong>${rawData.total_count.toLocaleString()}</strong>
                    </div>`;
                }
                
                if (rawData && rawData.failure_rate !== null && rawData.failure_rate !== undefined) {
                    html += `<div style="margin: 4px 0;">
                        <span style="color: #f48771;">●</span> 
                        Failure Rate: <strong>${rawData.failure_rate.toFixed(2)}%</strong>
                    </div>`;
                }
                
                if (rawData && rawData.avg_amount) {
                    html += `<div style="margin: 4px 0;">
                        <span style="color: #89d185;">●</span> 
                        Avg Amount: <strong>₹${rawData.avg_amount.toLocaleString()}</strong>
                    </div>`;
                }
                
                if (rawData && rawData.fraud_rate !== null && rawData.fraud_rate !== undefined) {
                    html += `<div style="margin: 4px 0;">
                        <span style="color: #ce9178;">●</span> 
                        Fraud Rate: <strong>${rawData.fraud_rate.toFixed(2)}%</strong>
                    </div>`;
                }
                
                html += `</div>`;
                return html;
            }
        },
        visualMap: {
            min: mapData.min_value,
            max: mapData.max_value,
            text: ['High', 'Low'],
            realtime: false,
            calculable: true,
            inRange: {
                color: mapData.color_scale
            },
            textStyle: {
                color: '#cccccc'
            },
            left: 'left',
            bottom: 50
        },
        series: [
            {
                name: mapData.metric_label,
                type: 'map',
                map: 'india',
                roam: true,
                emphasis: {
                    label: {
                        show: true,
                        color: '#ffffff',
                        fontSize: 14,
                        fontWeight: 'bold'
                    },
                    itemStyle: {
                        areaColor: '#007acc',
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }
                },
                select: {
                    label: {
                        show: true,
                        color: '#ffffff',
                        fontSize: 14
                    },
                    itemStyle: {
                        areaColor: '#1e8ad6'
                    }
                },
                itemStyle: {
                    borderColor: '#3e3e42',
                    borderWidth: 1,
                    areaColor: '#2d2d30'
                },
                label: {
                    show: true,  // Always show labels
                    fontSize: 11,
                    color: '#ffffff',
                    fontWeight: '600',
                    formatter: function(params) {
                        // Show state name and value
                        if (params.data && params.data.value) {
                            const value = params.data.value;
                            if (mapData.unit === '₹') {
                                return params.name + '\n₹' + value.toFixed(0);
                            } else if (mapData.unit === '%') {
                                return params.name + '\n' + value.toFixed(1) + '%';
                            } else {
                                return params.name + '\n' + value.toLocaleString();
                            }
                        }
                        return params.name;
                    }
                },
                data: seriesData
            }
        ]
    };

    // Set option and render
    try {
        chart.setOption(option);
        console.log('[MAP] Map rendered successfully');
    } catch (error) {
        console.error('[MAP] Failed to render map:', error);
        
        // Show error message in the container
        chartContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #f48771;">
                <i class="fas fa-exclamation-triangle" style="font-size: 48px; margin-bottom: 16px;"></i>
                <div style="font-size: 16px; font-weight: 600;">Map Rendering Failed</div>
                <div style="font-size: 13px; color: #858585; margin-top: 8px;">India map data not loaded</div>
                <div style="font-size: 12px; color: #858585; margin-top: 16px;">
                    Run: <code style="background: #2d2d30; padding: 4px 8px; border-radius: 4px;">node download-india-map.js</code>
                </div>
            </div>
        `;
        return null;
    }

    // Handle click events
    chart.on('click', function(params) {
        if (params.componentType === 'series') {
            const stateName = params.name;
            console.log('[MAP] Clicked state:', stateName);
            
            // Auto-generate drill-down query
            const drillDownQuery = `Analyze ${stateName} transactions in detail`;
            if (typeof chatInput !== 'undefined') {
                chatInput.value = drillDownQuery;
                showNotification(`Click "Send" to analyze ${stateName} in detail`, 'info');
            }
        }
    });

    // Responsive resize
    const resizeObserver = new ResizeObserver(() => {
        chart.resize();
    });
    resizeObserver.observe(chartContainer);

    return chart;
}

/**
 * Get color for value based on scale
 */
function getColorForValue(value, min, max, colorScale) {
    if (max === min) return colorScale[1];
    
    const ratio = (value - min) / (max - min);
    
    if (ratio < 0.33) return colorScale[0];
    if (ratio < 0.67) return colorScale[1];
    return colorScale[2];
}

/**
 * Format value with unit
 */
function formatValue(value, unit) {
    if (unit === '%') {
        return `${value.toFixed(2)}%`;
    } else if (unit === '₹') {
        return `₹${value.toLocaleString()}`;
    } else if (unit === 'transactions') {
        return value.toLocaleString();
    }
    return value.toLocaleString();
}

/**
 * Download map as image
 */
function downloadMap(button) {
    const card = button.closest('.map-card');
    const container = card.querySelector('.india-map-container');
    const chart = container.chartInstance;
    
    if (chart) {
        const url = chart.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#1e1e1e'
        });
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `india-map-${Date.now()}.png`;
        link.click();
        
        showNotification('Map downloaded successfully', 'success');
    }
}

/**
 * Toggle fullscreen mode
 */
function toggleMapFullscreen(button) {
    const card = button.closest('.map-card');
    const icon = button.querySelector('i');
    
    if (card.classList.contains('fullscreen')) {
        card.classList.remove('fullscreen');
        icon.classList.remove('fa-compress');
        icon.classList.add('fa-expand');
    } else {
        card.classList.add('fullscreen');
        icon.classList.remove('fa-expand');
        icon.classList.add('fa-compress');
        
        // Resize chart
        const container = card.querySelector('.india-map-container');
        if (container.chartInstance) {
            setTimeout(() => container.chartInstance.resize(), 100);
        }
    }
}

/**
 * Register India map with ECharts
 * This should be called once on page load
 */
function registerIndiaMap() {
    // Try to load local GeoJSON file first
    fetch('features/india-map-data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Local file not found');
            }
            return response.json();
        })
        .then(geoJson => {
            echarts.registerMap('india', geoJson);
            console.log('[MAP] India map registered successfully from local file');
            console.log(`[MAP] Loaded ${geoJson.features.length} states/UTs`);
        })
        .catch(error => {
            console.warn('[MAP] Failed to load local GeoJSON, using embedded simplified map');
            // Fallback to embedded simplified map
            registerSimplifiedIndiaMap();
        });
}

/**
 * Register simplified India map (fallback)
 */
function registerSimplifiedIndiaMap() {
    // Simplified India GeoJSON with major states
    const indiaGeoJSON = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Maharashtra"},
                "geometry": {"type": "Polygon", "coordinates": [[[73.7, 20.0], [77.0, 20.0], [77.0, 16.0], [73.7, 16.0], [73.7, 20.0]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Uttar Pradesh"},
                "geometry": {"type": "Polygon", "coordinates": [[[77.0, 30.5], [84.0, 30.5], [84.0, 24.0], [77.0, 24.0], [77.0, 30.5]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Karnataka"},
                "geometry": {"type": "Polygon", "coordinates": [[[74.0, 18.5], [78.5, 18.5], [78.5, 11.5], [74.0, 11.5], [74.0, 18.5]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Tamil Nadu"},
                "geometry": {"type": "Polygon", "coordinates": [[[76.5, 13.5], [80.5, 13.5], [80.5, 8.0], [76.5, 8.0], [76.5, 13.5]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Delhi"},
                "geometry": {"type": "Polygon", "coordinates": [[[76.8, 28.9], [77.4, 28.9], [77.4, 28.4], [76.8, 28.4], [76.8, 28.9]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Telangana"},
                "geometry": {"type": "Polygon", "coordinates": [[[77.0, 19.5], [81.0, 19.5], [81.0, 16.0], [77.0, 16.0], [77.0, 19.5]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Gujarat"},
                "geometry": {"type": "Polygon", "coordinates": [[[68.0, 24.5], [74.5, 24.5], [74.5, 20.0], [68.0, 20.0], [68.0, 24.5]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Andhra Pradesh"},
                "geometry": {"type": "Polygon", "coordinates": [[[77.0, 19.0], [84.5, 19.0], [84.5, 12.5], [77.0, 12.5], [77.0, 19.0]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "Rajasthan"},
                "geometry": {"type": "Polygon", "coordinates": [[[69.5, 30.0], [78.0, 30.0], [78.0, 23.0], [69.5, 23.0], [69.5, 30.0]]]}
            },
            {
                "type": "Feature",
                "properties": {"name": "West Bengal"},
                "geometry": {"type": "Polygon", "coordinates": [[[85.0, 27.5], [89.5, 27.5], [89.5, 21.5], [85.0, 21.5], [85.0, 27.5]]]}
            }
        ]
    };
    
    try {
        echarts.registerMap('india', indiaGeoJSON);
        console.log('[MAP] India map registered successfully (embedded simplified)');
    } catch (error) {
        console.error('[MAP] Failed to register India map:', error);
    }
}

// Auto-register map on load
if (typeof echarts !== 'undefined') {
    console.log('[MAP] ECharts detected, registering India map...');
    registerIndiaMap();
} else {
    console.error('[MAP] ECharts not loaded! Make sure echarts.min.js is included.');
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        renderIndiaMap,
        downloadMap,
        toggleMapFullscreen,
        registerIndiaMap
    };
}

// Make functions globally available
window.renderIndiaMap = renderIndiaMap;
window.downloadMap = downloadMap;
window.toggleMapFullscreen = toggleMapFullscreen;
