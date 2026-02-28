/**
 * InsightX Analytics - Apache ECharts Visualization System
 * Handles dynamic chart rendering from AI response data
 */

// Chart registry to track all chart instances
window.chartInstances = {};

// Color schemes
const COLOR_SCHEMES = {
    gradient: {
        primary: ['#6366f1', '#3b82f6'],
        success: ['#10b981', '#059669'],
        danger: ['#ef4444', '#dc2626'],
        warning: ['#f59e0b', '#d97706']
    },
    multi: ['#6366f1', '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444'],
    single: '#6366f1'
};

/**
 * Main function to render charts from AI response
 * @param {Object} responseData - Data from Flask backend
 * @param {string} containerId - DOM element ID to render chart
 */
function renderChartFromAIResponse(respo