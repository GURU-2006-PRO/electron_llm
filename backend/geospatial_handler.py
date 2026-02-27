"""
Geospatial Handler for India Map Visualization
Automatically generates India map data when state queries are detected
"""

import pandas as pd
from typing import Dict, List, Optional


# India state name mappings (handle variations)
INDIA_STATE_MAPPING = {
    # Standard names
    'andhra pradesh': 'Andhra Pradesh',
    'arunachal pradesh': 'Arunachal Pradesh',
    'assam': 'Assam',
    'bihar': 'Bihar',
    'chhattisgarh': 'Chhattisgarh',
    'goa': 'Goa',
    'gujarat': 'Gujarat',
    'haryana': 'Haryana',
    'himachal pradesh': 'Himachal Pradesh',
    'jharkhand': 'Jharkhand',
    'karnataka': 'Karnataka',
    'kerala': 'Kerala',
    'madhya pradesh': 'Madhya Pradesh',
    'maharashtra': 'Maharashtra',
    'manipur': 'Manipur',
    'meghalaya': 'Meghalaya',
    'mizoram': 'Mizoram',
    'nagaland': 'Nagaland',
    'odisha': 'Odisha',
    'punjab': 'Punjab',
    'rajasthan': 'Rajasthan',
    'sikkim': 'Sikkim',
    'tamil nadu': 'Tamil Nadu',
    'telangana': 'Telangana',
    'tripura': 'Tripura',
    'uttar pradesh': 'Uttar Pradesh',
    'uttarakhand': 'Uttarakhand',
    'west bengal': 'West Bengal',
    
    # Union Territories
    'andaman and nicobar islands': 'Andaman and Nicobar Islands',
    'chandigarh': 'Chandigarh',
    'dadra and nagar haveli and daman and diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'delhi': 'Delhi',
    'jammu and kashmir': 'Jammu and Kashmir',
    'ladakh': 'Ladakh',
    'lakshadweep': 'Lakshadweep',
    'puducherry': 'Puducherry',
    
    # Common abbreviations
    'ap': 'Andhra Pradesh',
    'ar': 'Arunachal Pradesh',
    'as': 'Assam',
    'br': 'Bihar',
    'cg': 'Chhattisgarh',
    'ga': 'Goa',
    'gj': 'Gujarat',
    'hr': 'Haryana',
    'hp': 'Himachal Pradesh',
    'jh': 'Jharkhand',
    'ka': 'Karnataka',
    'kl': 'Kerala',
    'mp': 'Madhya Pradesh',
    'mh': 'Maharashtra',
    'mn': 'Manipur',
    'ml': 'Meghalaya',
    'mz': 'Mizoram',
    'nl': 'Nagaland',
    'or': 'Odisha',
    'pb': 'Punjab',
    'rj': 'Rajasthan',
    'sk': 'Sikkim',
    'tn': 'Tamil Nadu',
    'tg': 'Telangana',
    'tr': 'Tripura',
    'up': 'Uttar Pradesh',
    'uk': 'Uttarakhand',
    'wb': 'West Bengal',
}


class GeospatialHandler:
    """Handles geospatial queries and map generation"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.state_column = self._find_state_column()
    
    def _find_state_column(self) -> Optional[str]:
        """Find the state column in dataset"""
        for col in self.df.columns:
            col_lower = col.lower()
            if 'state' in col_lower:
                return col
        return None
    
    def is_geospatial_query(self, query: str, query_spec: Dict) -> bool:
        """
        Detect if query is about states/geography
        
        Returns True if:
        - Query mentions "state" or "states"
        - Query mentions specific state names
        - Group by column is state-related
        """
        query_lower = query.lower()
        
        # Check for state keywords
        state_keywords = ['state', 'states', 'region', 'regions', 'geography', 'map', 'location']
        if any(keyword in query_lower for keyword in state_keywords):
            return True
        
        # Check if grouping by state
        group_col = query_spec.get('group_by_column')
        if group_col and isinstance(group_col, str):
            if 'state' in group_col.lower():
                return True
        
        # Check if any state name mentioned
        for state in INDIA_STATE_MAPPING.values():
            if state.lower() in query_lower:
                return True
        
        return False
    
    def generate_map_data(self, result_df: pd.DataFrame, metric: str = 'total_count') -> Dict:
        """
        Generate India map data from query results
        
        Args:
            result_df: DataFrame with state-wise data
            metric: Metric to visualize (total_count, failure_rate_pct, etc.)
        
        Returns:
            Dict with map configuration for ECharts
        """
        if self.state_column is None:
            return None
        
        # Normalize state names
        map_data = []
        for _, row in result_df.iterrows():
            state_raw = str(row.get(self.state_column, ''))
            state_normalized = self._normalize_state_name(state_raw)
            
            if state_normalized:
                value = row.get(metric, 0)
                map_data.append({
                    'name': state_normalized,
                    'value': float(value) if pd.notna(value) else 0,
                    'raw_data': {
                        'total_count': int(row.get('total_count', 0)),
                        'failure_rate': float(row.get('failure_rate_pct', 0)) if 'failure_rate_pct' in row else None,
                        'avg_amount': float(row.get('avg_amount', 0)) if 'avg_amount' in row else None,
                        'fraud_rate': float(row.get('fraud_flag_rate_pct', 0)) if 'fraud_flag_rate_pct' in row else None
                    }
                })
        
        # Determine metric type for color scale
        metric_config = self._get_metric_config(metric)
        
        return {
            'type': 'india_map',
            'data': map_data,
            'metric': metric,
            'metric_label': metric_config['label'],
            'color_scale': metric_config['color_scale'],
            'min_value': min([d['value'] for d in map_data]) if map_data else 0,
            'max_value': max([d['value'] for d in map_data]) if map_data else 100,
            'unit': metric_config['unit']
        }
    
    def _normalize_state_name(self, state: str) -> Optional[str]:
        """Normalize state name to standard format"""
        if not state or pd.isna(state):
            return None
        
        state_lower = state.lower().strip()
        return INDIA_STATE_MAPPING.get(state_lower, state)
    
    def _get_metric_config(self, metric: str) -> Dict:
        """Get configuration for different metrics"""
        configs = {
            'total_count': {
                'label': 'Transaction Volume',
                'unit': 'transactions',
                'color_scale': ['#e3f2fd', '#2196f3', '#0d47a1']  # Blue scale
            },
            'failure_rate_pct': {
                'label': 'Failure Rate',
                'unit': '%',
                'color_scale': ['#fff3e0', '#ff9800', '#e65100']  # Orange to red
            },
            'fraud_flag_rate_pct': {
                'label': 'Fraud Rate',
                'unit': '%',
                'color_scale': ['#ffebee', '#f44336', '#b71c1c']  # Red scale
            },
            'avg_amount': {
                'label': 'Average Amount',
                'unit': '₹',
                'color_scale': ['#e8f5e9', '#4caf50', '#1b5e20']  # Green scale
            }
        }
        
        return configs.get(metric, {
            'label': metric.replace('_', ' ').title(),
            'unit': '',
            'color_scale': ['#e0e0e0', '#757575', '#212121']  # Gray scale
        })
    
    def get_state_statistics(self) -> Dict:
        """Get overall state-wise statistics"""
        if self.state_column is None:
            return None
        
        stats = self.df.groupby(self.state_column).agg({
            'transaction id': 'count',
            'transaction_status': lambda x: (x == 'FAILED').mean() * 100 if 'transaction_status' in self.df.columns else 0,
            'fraud_flag': lambda x: x.mean() * 100 if 'fraud_flag' in self.df.columns else 0
        }).reset_index()
        
        stats.columns = [self.state_column, 'total_count', 'failure_rate', 'fraud_rate']
        
        # Find top and bottom states
        top_volume = stats.nlargest(5, 'total_count')
        top_failure = stats.nlargest(5, 'failure_rate')
        
        return {
            'total_states': len(stats),
            'top_volume_states': top_volume.to_dict('records'),
            'top_failure_states': top_failure.to_dict('records'),
            'overall_stats': {
                'total_transactions': int(stats['total_count'].sum()),
                'avg_failure_rate': float(stats['failure_rate'].mean()),
                'avg_fraud_rate': float(stats['fraud_rate'].mean())
            }
        }


def enhance_with_geospatial(query: str, query_spec: Dict, result_df: pd.DataFrame, df: pd.DataFrame) -> Optional[Dict]:
    """
    Main function to enhance query results with geospatial data
    
    Returns:
        Dict with map data if query is geospatial, None otherwise
    """
    handler = GeospatialHandler(df)
    
    # Check if this is a geospatial query
    if not handler.is_geospatial_query(query, query_spec):
        return None
    
    # Determine which metric to visualize based on query and available columns
    query_lower = query.lower()
    metrics = query_spec.get('metrics', [])
    
    # Check what columns are in result_df
    available_cols = result_df.columns.tolist()
    
    # Priority 1: Check query intent
    if 'amount' in query_lower or 'value' in query_lower or 'revenue' in query_lower:
        if 'avg_amount' in available_cols:
            metric = 'avg_amount'
        elif 'total_amount' in available_cols:
            metric = 'total_amount'
        else:
            metric = 'total_count'
    elif 'failure' in query_lower or 'failed' in query_lower:
        if 'failure_rate_pct' in available_cols:
            metric = 'failure_rate_pct'
        else:
            metric = 'total_count'
    elif 'fraud' in query_lower:
        if 'fraud_flag_rate_pct' in available_cols:
            metric = 'fraud_flag_rate_pct'
        else:
            metric = 'total_count'
    else:
        # Priority 2: Check metrics in query_spec
        if 'failure_rate' in metrics and 'failure_rate_pct' in available_cols:
            metric = 'failure_rate_pct'
        elif 'fraud_rate' in metrics and 'fraud_flag_rate_pct' in available_cols:
            metric = 'fraud_flag_rate_pct'
        elif 'avg_amount' in metrics and 'avg_amount' in available_cols:
            metric = 'avg_amount'
        elif 'avg_amount' in available_cols:
            metric = 'avg_amount'
        else:
            metric = 'total_count'
    
    print(f"[GEOSPATIAL] Selected metric: {metric} from available columns: {available_cols}")
    
    # Generate map data
    map_data = handler.generate_map_data(result_df, metric)
    
    return map_data
