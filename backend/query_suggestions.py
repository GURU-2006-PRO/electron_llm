"""
Query Suggestion and Auto-Complete System
"""

import pandas as pd
from typing import List, Dict


class QuerySuggestionEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.columns = df.columns.tolist()
        self._build_templates()
    
    def _build_templates(self):
        """Build query templates"""
        self.categorical_cols = []
        self.numeric_cols = []
        
        for col in self.columns:
            if self.df[col].dtype in ['object', 'string']:
                if self.df[col].nunique() < 50:
                    self.categorical_cols.append(col)
            elif self.df[col].dtype in ['float64', 'int64']:
                self.numeric_cols.append(col)
    
    def get_suggestions(self, partial_query: str = "", limit: int = 10) -> List[Dict]:
        """Get query suggestions based on partial input"""
        suggestions = []
        
        # Example queries
        examples = [
            {
                "query": "What is the overall failure rate?",
                "category": "Overview",
                "description": "Get platform-wide failure statistics"
            },
            {
                "query": "Compare Android vs iOS failure rates",
                "category": "Comparison",
                "description": "Compare device types"
            },
            {
                "query": "Show top 10 banks by transaction volume",
                "category": "Ranking",
                "description": "Identify highest volume banks"
            },
            {
                "query": "Analyze weekend vs weekday transactions",
                "category": "Comparison",
                "description": "Compare time periods"
            },
            {
                "query": "What are the most common fraud patterns?",
                "category": "Analysis",
                "description": "Identify fraud trends"
            },
            {
                "query": "Show transactions above 10000 rupees",
                "category": "Filtering",
                "description": "Filter high-value transactions"
            },
            {
                "query": "Which merchant category has highest failure rate?",
                "category": "Analysis",
                "description": "Analyze merchant performance"
            },
            {
                "query": "Compare 3G vs 4G vs 5G network performance",
                "category": "Comparison",
                "description": "Network type analysis"
            },
            {
                "query": "Top 20 transactions by amount",
                "category": "Ranking",
                "description": "List highest value transactions"
            },
            {
                "query": "Analyze failure rate by hour of day",
                "category": "Trend",
                "description": "Time-based pattern analysis"
            }
        ]
        
        # Filter by partial query
        if partial_query:
            query_lower = partial_query.lower()
            for ex in examples:
                if query_lower in ex["query"].lower():
                    suggestions.append(ex)
        else:
            suggestions = examples
        
        return suggestions[:limit]
    
    def get_follow_up_suggestions(self, previous_query: str, result_data: dict) -> List[str]:
        """Generate contextual follow-up questions"""
        follow_ups = []
        
        query_lower = previous_query.lower()
        
        # Based on query type
        if 'failure' in query_lower:
            follow_ups.extend([
                "What are the main causes of these failures?",
                "Which time period has the highest failure rate?",
                "Compare failure rates across different banks"
            ])
        
        if 'compare' in query_lower or 'vs' in query_lower:
            follow_ups.extend([
                "Show me the detailed breakdown",
                "What is the statistical significance of this difference?",
                "Are there any anomalies in this comparison?"
            ])
        
        if 'top' in query_lower or 'highest' in query_lower:
            follow_ups.extend([
                "Show me the bottom performers",
                "What insights can we draw from this ranking?",
                "Compare the top 3 in detail"
            ])
        
        if 'fraud' in query_lower:
            follow_ups.extend([
                "Which banks have the highest fraud rate?",
                "What time of day sees most fraud?",
                "Compare fraud rates by transaction type"
            ])
        
        # Generic follow-ups
        follow_ups.extend([
            "Show me trends over time",
            "Break this down by category",
            "What are the anomalies here?"
        ])
        
        return follow_ups[:5]
    
    def suggest_typo_correction(self, query: str) -> Dict:
        """Suggest corrections for common typos"""
        corrections = {
            'merchent': 'merchant',
            'trasaction': 'transaction',
            'failur': 'failure',
            'succes': 'success',
            'comparision': 'comparison',
            'analize': 'analyze',
            'recieve': 'receive',
            'reciver': 'receiver'
        }
        
        query_lower = query.lower()
        for typo, correct in corrections.items():
            if typo in query_lower:
                corrected = query_lower.replace(typo, correct)
                return {
                    "has_typo": True,
                    "original": query,
                    "corrected": corrected,
                    "suggestion": f"Did you mean '{corrected}'?"
                }
        
        return {"has_typo": False}
    
    def check_typo(self, query: str) -> Dict:
        """Alias for suggest_typo_correction for compatibility"""
        return self.suggest_typo_correction(query)

