"""
Backend Chart Generator using Plotly
Generates charts as base64 encoded images
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
from io import BytesIO


class ChartGenerator:
    """Generate charts on the backend using Plotly"""
    
    def __init__(self):
        self.colors = {
            'primary': '#007acc',
            'secondary': '#1e8ad6',
            'success': '#89d185',
            'warning': '#cca700',
            'error': '#f48771',
            'gradient': ['#007acc', '#1e8ad6', '#4a9eff', '#6bb3ff']
        }
        
        self.template = {
            'layout': {
                'paper_bgcolor': '#1e1e1e',
                'plot_bgcolor': '#2d2d30',
                'font': {'color': '#cccccc', 'family': 'Inter, sans-serif'},
                'title': {'font': {'size': 16, 'color': '#cccccc'}},
                'xaxis': {
                    'gridcolor': '#3e3e42',
                    'linecolor': '#3e3e42',
                    'tickfont': {'color': '#858585'}
                },
                'yaxis': {
                    'gridcolor': '#3e3e42',
                    'linecolor': '#3e3e42',
                    'tickfont': {'color': '#858585'}
                }
            }
        }
    
    def generate_chart(self, data, chart_type, title="Chart", x_label=None, y_label=None):
        """
        Generate a chart and return as base64 encoded image
        
        Args:
            data: List of dicts or DataFrame
            chart_type: 'bar', 'line', 'pie', 'area', 'horizontal_bar'
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            
        Returns:
            dict with 'image' (base64), 'type', 'title'
        """
        try:
            # Convert to DataFrame if needed
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data
            
            if df.empty:
                return {"error": "No data to visualize"}
            
            # Get first column as labels, first numeric column as values
            label_col = df.columns[0]
            value_col = None
            for col in df.columns[1:]:
                if pd.api.types.is_numeric_dtype(df[col]):
                    value_col = col
                    break
            
            if value_col is None:
                return {"error": "No numeric data found"}
            
            labels = df[label_col].astype(str).tolist()
            values = df[value_col].tolist()
            
            # Generate chart based on type
            if chart_type == 'bar' or chart_type == 'vertical_bar':
                fig = self._create_bar_chart(labels, values, title, x_label or label_col, y_label or value_col)
            elif chart_type == 'horizontal_bar':
                fig = self._create_horizontal_bar_chart(labels, values, title, x_label or value_col, y_label or label_col)
            elif chart_type == 'line':
                fig = self._create_line_chart(labels, values, title, x_label or label_col, y_label or value_col)
            elif chart_type == 'area':
                fig = self._create_area_chart(labels, values, title, x_label or label_col, y_label or value_col)
            elif chart_type == 'pie' or chart_type == 'donut':
                fig = self._create_pie_chart(labels, values, title, is_donut=(chart_type == 'donut'))
            else:
                return {"error": f"Unknown chart type: {chart_type}"}
            
            # Convert to base64 image
            img_bytes = fig.to_image(format="png", width=1000, height=600)
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            return {
                "image": f"data:image/png;base64,{img_base64}",
                "type": chart_type,
                "title": title,
                "data_points": len(labels)
            }
            
        except Exception as e:
            print(f"[ERROR] Chart generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _create_bar_chart(self, labels, values, title, x_label, y_label):
        """Create vertical bar chart"""
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=values,
                marker=dict(
                    color=self.colors['primary'],
                    line=dict(color=self.colors['secondary'], width=1)
                ),
                text=values,
                texttemplate='%{text:,.0f}',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            **self.template['layout'],
            showlegend=False,
            height=600
        )
        
        return fig
    
    def _create_horizontal_bar_chart(self, labels, values, title, x_label, y_label):
        """Create horizontal bar chart"""
        fig = go.Figure(data=[
            go.Bar(
                x=values,
                y=labels,
                orientation='h',
                marker=dict(
                    color=self.colors['primary'],
                    line=dict(color=self.colors['secondary'], width=1)
                ),
                text=values,
                texttemplate='%{text:,.0f}',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            **self.template['layout'],
            showlegend=False,
            height=600
        )
        
        return fig
    
    def _create_line_chart(self, labels, values, title, x_label, y_label):
        """Create line chart"""
        fig = go.Figure(data=[
            go.Scatter(
                x=labels,
                y=values,
                mode='lines+markers',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=self.colors['secondary']),
                fill=None
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            **self.template['layout'],
            showlegend=False,
            height=600
        )
        
        return fig
    
    def _create_area_chart(self, labels, values, title, x_label, y_label):
        """Create area chart"""
        fig = go.Figure(data=[
            go.Scatter(
                x=labels,
                y=values,
                mode='lines',
                line=dict(color=self.colors['primary'], width=3),
                fill='tozeroy',
                fillcolor='rgba(0, 122, 204, 0.3)'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            **self.template['layout'],
            showlegend=False,
            height=600
        )
        
        return fig
    
    def _create_pie_chart(self, labels, values, title, is_donut=False):
        """Create pie/donut chart"""
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4 if is_donut else 0,
                marker=dict(colors=self.colors['gradient']),
                textinfo='label+percent',
                textfont=dict(color='#cccccc')
            )
        ])
        
        fig.update_layout(
            title=title,
            **self.template['layout'],
            showlegend=True,
            legend=dict(
                font=dict(color='#858585'),
                bgcolor='rgba(0,0,0,0)'
            ),
            height=600
        )
        
        return fig


# Global instance
chart_generator = ChartGenerator()
