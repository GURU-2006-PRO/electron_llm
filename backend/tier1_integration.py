"""
TIER 1 Features Integration
Integrates all 5 critical features into the main application
"""

from statistical_significance import (
    add_significance_to_comparison,
    calculate_sample_size_adequacy,
    calculate_proportion_test
)
from anomaly_detector import scan_for_anomalies
from methodology_explainer import MethodologyExplainer
from query_suggestions import QuerySuggestionEngine
import pandas as pd
from typing import Dict, List


class Tier1FeatureManager:
    """Manages all TIER 1 features"""
    
    def __init__(self, df: pd.DataFrame, global_stats: Dict):
        self.df = df
        self.global_stats = global_stats
        self.conversation_context = []
        self.anomalies_cache = None
        self.suggestion_engine = QuerySuggestionEngine(df)
        self.methodology_explainer = MethodologyExplainer()
    
    # ===== 1. STATISTICAL SIGNIFICANCE =====
    
    def add_statistical_tests(self, result_df: pd.DataFrame, query_spec: Dict) -> Dict:
        """Add statistical significance testing to results"""
        operation = query_spec.get('operation')
        
        if operation not in ['group_by_single', 'filter_then_group', 'comparison']:
            return None
        
        # Check if this is a comparison
        if len(result_df) < 2:
            return None
        
        group_col = query_spec.get('group_by_column')
        metrics = query_spec.get('metrics', [])
        
        # Determine metric type
        if 'failure_rate' in metrics or 'fraud_rate' in metrics:
            metric_type = 'proportion'
            metric_col = 'failure_rate_pct' if 'failure_rate' in metrics else 'fraud_flag_rate_pct'
        else:
            metric_type = 'mean'
            metric_col = 'avg_amount'
        
        # Add significance tests
        significance_results = add_significance_to_comparison(
            result_df, 
            group_col if isinstance(group_col, str) else group_col[0],
            metric_col,
            metric_type
        )
        
        # Add sample size adequacy
        for idx, row in result_df.iterrows():
            n = row.get('total_count', 0)
            adequacy = calculate_sample_size_adequacy(n)
            result_df.at[idx, 'sample_adequacy'] = adequacy['adequacy']
            result_df.at[idx, 'confidence'] = adequacy['confidence']
        
        return significance_results
    
    # ===== 2. ANOMALY DETECTION =====
    
    def get_anomalies(self, force_refresh: bool = False) -> List[Dict]:
        """Get detected anomalies (cached)"""
        if self.anomalies_cache is None or force_refresh:
            self.anomalies_cache = scan_for_anomalies(self.df, self.global_stats)
        return self.anomalies_cache
    
    def get_top_anomaly(self) -> Dict:
        """Get the most severe anomaly"""
        anomalies = self.get_anomalies()
        return anomalies[0] if anomalies else None
    
    # ===== 3. QUERY AUTO-COMPLETE =====
    
    def get_query_suggestions(self, partial_query: str) -> List[Dict]:
        """Get query suggestions for auto-complete"""
        return self.suggestion_engine.get_suggestions(partial_query, limit=8)
    
    def check_typo(self, query: str) -> Dict:
        """Check for typos and suggest corrections"""
        return self.suggestion_engine.check_typo(query)
    
    # ===== 4. METHODOLOGY EXPLAINER =====
    
    def explain_methodology(self, query_spec: Dict, result_df: pd.DataFrame) -> Dict:
        """Generate methodology explanation"""
        return self.methodology_explainer.explain_query_execution(
            query_spec, 
            result_df, 
            self.df
        )
    
    def explain_calculation(self, metric: str, value: float, context: Dict) -> Dict:
        """Explain how a specific metric was calculated"""
        return self.methodology_explainer.explain_metric_calculation(
            metric, 
            value, 
            context
        )
    
    # ===== 5. CONTEXT MEMORY =====
    
    def add_to_context(self, query: str, entities: Dict):
        """Add query to conversation context"""
        self.conversation_context.append({
            'query': query,
            'entities': entities,
            'timestamp': pd.Timestamp.now()
        })
        
        # Keep last 3 queries
        if len(self.conversation_context) > 3:
            self.conversation_context = self.conversation_context[-3:]
    
    def expand_query_with_context(self, query: str) -> str:
        """Expand incomplete query using context"""
        if not self.conversation_context:
            return query
        
        query_lower = query.lower()
        
        # Check for follow-up patterns
        follow_up_patterns = [
            'what about', 'how about', 'and', 'also', 
            'compare', 'versus', 'vs', 'them', 'it', 'that'
        ]
        
        is_follow_up = any(pattern in query_lower for pattern in follow_up_patterns)
        
        if not is_follow_up:
            return query
        
        # Get last context
        last_context = self.conversation_context[-1]
        last_entities = last_context['entities']
        
        # Expand query
        expanded = query
        
        # Handle "what about X" pattern
        if 'what about' in query_lower or 'how about' in query_lower:
            # Extract new entity
            parts = query_lower.split('about')
            if len(parts) > 1:
                new_entity = parts[1].strip().rstrip('?')
                
                # Use same structure as last query
                last_query = last_context['query']
                
                # Replace old entity with new
                for key, value in last_entities.items():
                    if isinstance(value, str):
                        expanded = last_query.replace(value, new_entity)
                        break
        
        # Handle "compare them" pattern
        elif 'compare' in query_lower and ('them' in query_lower or 'both' in query_lower):
            # Get entities from last 2 queries
            if len(self.conversation_context) >= 2:
                entity1 = self.conversation_context[-2]['entities'].get('value')
                entity2 = self.conversation_context[-1]['entities'].get('value')
                
                if entity1 and entity2:
                    expanded = f"Compare {entity1} vs {entity2}"
        
        return expanded
    
    def get_context_indicator(self) -> str:
        """Get context indicator for UI"""
        if not self.conversation_context:
            return None
        
        last_context = self.conversation_context[-1]
        entities = last_context['entities']
        
        if entities:
            entity_str = ', '.join([f"{k}: {v}" for k, v in entities.items()])
            return f"📎 Context: {entity_str}"
        
        return None
    
    # ===== COMBINED ENHANCEMENT =====
    
    def enhance_insight(self, insight: Dict, query_spec: Dict, result_df: pd.DataFrame) -> Dict:
        """
        Enhance insight with all TIER 1 features
        
        Returns enhanced insight with:
        - Statistical significance
        - Methodology explanation
        - Sample size warnings
        - Context indicators
        """
        enhanced = insight.copy()
        
        # 1. Add statistical significance
        if result_df is not None and len(result_df) >= 2:
            sig_tests = self.add_statistical_tests(result_df, query_spec)
            if sig_tests:
                enhanced['statistical_significance'] = sig_tests
        
        # 2. Add methodology
        methodology = self.explain_methodology(query_spec, result_df)
        enhanced['methodology'] = methodology
        
        # 3. Add sample size warnings
        if result_df is not None:
            total_rows = result_df.get('total_count', pd.Series([0])).sum()
            adequacy = calculate_sample_size_adequacy(int(total_rows))
            if adequacy['warning']:
                enhanced['data_quality_warning'] = adequacy['warning']
        
        # 4. Add context indicator
        context_indicator = self.get_context_indicator()
        if context_indicator:
            enhanced['context'] = context_indicator
        
        return enhanced
