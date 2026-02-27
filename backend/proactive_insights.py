"""
Proactive Insights Generator
Automatically suggests follow-up questions and identifies interesting patterns
"""

from typing import List, Dict
import pandas as pd


class ProactiveInsightGenerator:
    """Generates proactive insights and suggestions"""
    
    def __init__(self, df: pd.DataFrame, global_stats: dict):
        self.df = df
        self.global_stats = global_stats
    
    def generate_follow_up_questions(self, query: str, result_df: pd.DataFrame, 
                                    query_spec: dict) -> List[str]:
        """Generate smart follow-up questions based on results"""
        
        follow_ups = []
        query_lower = query.lower()
        operation = query_spec.get('operation', '')
        
        # Based on query intent
        if 'failure' in query_lower or 'failed' in query_lower:
            follow_ups.extend([
                "What are the root causes of these failures?",
                "Which time period has the highest failure rate?",
                "How do failure rates compare across different networks?",
                "Are there any seasonal patterns in failures?"
            ])
        
        if 'compare' in query_lower or 'vs' in query_lower:
            follow_ups.extend([
                "What is the statistical significance of this difference?",
                "Show me the detailed breakdown by subcategory",
                "Are there any anomalies in this comparison?",
                "How has this comparison changed over time?"
            ])
        
        if 'top' in query_lower or 'highest' in query_lower or 'best' in query_lower:
            follow_ups.extend([
                "Show me the bottom performers for comparison",
                "What makes the top performer different?",
                "Are there any common patterns among top performers?",
                "How stable are these rankings over time?"
            ])
        
        if 'fraud' in query_lower:
            follow_ups.extend([
                "Which merchant categories have highest fraud rates?",
                "What time of day sees the most fraud attempts?",
                "Are there geographic patterns in fraud?",
                "How effective is our fraud detection?"
            ])
        
        if 'amount' in query_lower or 'transaction' in query_lower:
            follow_ups.extend([
                "How does this vary by transaction type?",
                "What is the trend over the past week?",
                "Are there any unusual spikes or drops?",
                "Compare this across different user segments"
            ])
        
        # Based on operation type
        if operation == 'group_by_single':
            group_col = query_spec.get('group_by_column')
            follow_ups.append(f"Break down {group_col} by another dimension")
            follow_ups.append(f"Show trends in {group_col} over time")
        
        # Generic valuable questions
        follow_ups.extend([
            "What actionable recommendations can you provide?",
            "Show me the data quality and confidence level",
            "Are there any hidden patterns I should know about?"
        ])
        
        # Remove duplicates and limit
        follow_ups = list(dict.fromkeys(follow_ups))
        return follow_ups[:6]
    
    def generate_proactive_alerts(self, result_df: pd.DataFrame, 
                                  query_spec: dict) -> List[Dict]:
        """Generate proactive alerts about interesting findings"""
        
        alerts = []
        
        # Check for high failure rates
        if 'failure_rate_pct' in result_df.columns:
            high_failure = result_df[result_df['failure_rate_pct'] > 10]
            if len(high_failure) > 0:
                for _, row in high_failure.head(3).iterrows():
                    category = row[result_df.columns[0]]
                    rate = row['failure_rate_pct']
                    alerts.append({
                        "type": "warning",
                        "severity": "high" if rate > 15 else "medium",
                        "title": "High Failure Rate Detected",
                        "message": f"{category} has a {rate:.1f}% failure rate (platform avg: {self.global_stats['overall_failure_rate_pct']}%)",
                        "action": f"Investigate failures in {category}",
                        "icon": "exclamation-triangle"
                    })
        
        # Check for high fraud rates
        if 'fraud_flag_rate_pct' in result_df.columns:
            high_fraud = result_df[result_df['fraud_flag_rate_pct'] > 5]
            if len(high_fraud) > 0:
                for _, row in high_fraud.head(2).iterrows():
                    category = row[result_df.columns[0]]
                    rate = row['fraud_flag_rate_pct']
                    alerts.append({
                        "type": "danger",
                        "severity": "high",
                        "title": "Elevated Fraud Activity",
                        "message": f"{category} shows {rate:.1f}% fraud flag rate",
                        "action": f"Review fraud patterns in {category}",
                        "icon": "shield-alt"
                    })
        
        # Check for unusual volumes
        if 'total_count' in result_df.columns:
            mean_count = result_df['total_count'].mean()
            std_count = result_df['total_count'].std()
            
            unusual = result_df[result_df['total_count'] > mean_count + 2*std_count]
            if len(unusual) > 0:
                for _, row in unusual.head(2).iterrows():
                    category = row[result_df.columns[0]]
                    count = row['total_count']
                    alerts.append({
                        "type": "info",
                        "severity": "medium",
                        "title": "Unusually High Volume",
                        "message": f"{category} has {count:,} transactions (2x above average)",
                        "action": f"Analyze why {category} has high volume",
                        "icon": "chart-line"
                    })
        
        return alerts[:5]
    
    def suggest_related_analyses(self, query: str, query_spec: dict) -> List[Dict]:
        """Suggest related analyses users might find valuable"""
        
        suggestions = []
        query_lower = query.lower()
        
        # Suggest time-based analysis
        if 'time' not in query_lower and 'hour' not in query_lower and 'day' not in query_lower:
            suggestions.append({
                "title": "Time-Based Analysis",
                "description": "See how this metric varies by hour of day or day of week",
                "query": f"{query} broken down by time",
                "benefit": "Identify peak hours and time-based patterns",
                "icon": "clock"
            })
        
        # Suggest geographic analysis
        if 'state' not in query_lower and 'location' not in query_lower:
            suggestions.append({
                "title": "Geographic Analysis",
                "description": "Analyze this metric across different states",
                "query": f"{query} by state",
                "benefit": "Discover regional variations and opportunities",
                "icon": "map-marked-alt"
            })
        
        # Suggest cohort analysis
        if 'age' not in query_lower and 'group' not in query_lower:
            suggestions.append({
                "title": "User Segment Analysis",
                "description": "Compare across different age groups",
                "query": f"{query} by age group",
                "benefit": "Understand user behavior patterns",
                "icon": "users"
            })
        
        # Suggest trend analysis
        suggestions.append({
            "title": "Trend Analysis",
            "description": "See how this has changed over time",
            "query": f"Show trend of {query} over past 30 days",
            "benefit": "Identify growth or decline patterns",
            "icon": "chart-area"
        })
        
        # Suggest root cause analysis
        if 'failure' in query_lower or 'problem' in query_lower:
            suggestions.append({
                "title": "Root Cause Analysis",
                "description": "Deep dive into what's causing this issue",
                "query": f"What are the root causes of {query}",
                "benefit": "Find actionable solutions",
                "icon": "search"
            })
        
        return suggestions[:4]
    
    def generate_insight_summary(self, result_df: pd.DataFrame, 
                                query_spec: dict) -> Dict:
        """Generate a quick insight summary"""
        
        summary = {
            "key_finding": "",
            "notable_points": [],
            "action_items": []
        }
        
        # Identify key finding
        if len(result_df) > 0:
            first_col = result_df.columns[0]
            
            if 'failure_rate_pct' in result_df.columns:
                top_row = result_df.nlargest(1, 'failure_rate_pct').iloc[0]
                summary["key_finding"] = f"{top_row[first_col]} has the highest failure rate at {top_row['failure_rate_pct']:.1f}%"
                
                if top_row['failure_rate_pct'] > self.global_stats['overall_failure_rate_pct'] * 1.5:
                    summary["action_items"].append(f"Investigate {top_row[first_col]} failures urgently")
            
            elif 'total_count' in result_df.columns:
                top_row = result_df.nlargest(1, 'total_count').iloc[0]
                summary["key_finding"] = f"{top_row[first_col]} leads with {top_row['total_count']:,} transactions"
            
            # Notable points
            if len(result_df) >= 3:
                summary["notable_points"].append(f"Analyzed {len(result_df)} categories")
                
                if 'failure_rate_pct' in result_df.columns:
                    avg_rate = result_df['failure_rate_pct'].mean()
                    summary["notable_points"].append(f"Average failure rate: {avg_rate:.1f}%")
                
                if 'avg_amount' in result_df.columns:
                    avg_amt = result_df['avg_amount'].mean()
                    summary["notable_points"].append(f"Average transaction: ₹{avg_amt:,.0f}")
        
        return summary
