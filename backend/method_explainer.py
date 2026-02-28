"""
Methodology Explainer - Shows step-by-step how insights were generated
"""

from typing import Dict, List


class MethodologyExplainer:
    """Explains the methodology used to generate insights"""
    
    @staticmethod
    def explain_query_execution(query_spec: dict, result_df, original_df) -> Dict:
        """Generate step-by-step explanation of query execution"""
        
        steps = []
        operation = query_spec.get('operation', 'unknown')
        
        # Step 1: Data Loading
        steps.append({
            "step": 1,
            "action": "Data Loading",
            "description": f"Loaded {len(original_df):,} transaction records from dataset",
            "details": f"Dataset contains {len(original_df.columns)} columns",
            "icon": "database"
        })
        
        # Step 2: Filtering
        if query_spec.get('filter_conditions'):
            filters = query_spec['filter_conditions']
            steps.append({
                "step": 2,
                "action": "Applied Filters",
                "description": f"Filtered data using {len(filters)} condition(s)",
                "details": f"Filters: {', '.join(filters)}",
                "rows_before": len(original_df),
                "rows_after": len(result_df) if operation == 'filter_segment' else "N/A",
                "icon": "filter"
            })
        
        # Step 3: Grouping/Aggregation
        if operation in ['group_by_single', 'filter_then_group']:
            group_col = query_spec.get('group_by_column')
            metrics = query_spec.get('metrics', [])
            
            if isinstance(group_col, list):
                group_desc = f"Grouped by {len(group_col)} columns: {', '.join(group_col)}"
            else:
                group_desc = f"Grouped by: {group_col}"
            
            steps.append({
                "step": len(steps) + 1,
                "action": "Grouping & Aggregation",
                "description": group_desc,
                "details": f"Calculated metrics: {', '.join(metrics)}",
                "groups_created": len(result_df),
                "icon": "layer-group"
            })
        
        elif operation == 'top_n_records':
            limit = query_spec.get('limit', 20)
            sort_by = query_spec.get('sort_by', 'unknown')
            
            steps.append({
                "step": len(steps) + 1,
                "action": "Sorting & Selection",
                "description": f"Sorted by {sort_by} and selected top {limit} records",
                "details": f"Order: {'Ascending' if query_spec.get('sort_ascending') else 'Descending'}",
                "icon": "sort-amount-down"
            })
        
        # Step 4: Statistical Analysis
        steps.append({
            "step": len(steps) + 1,
            "action": "Statistical Analysis",
            "description": "Performed statistical tests and anomaly detection",
            "details": "Calculated p-values, confidence intervals, and identified outliers",
            "icon": "chart-line"
        })
        
        # Step 5: Insight Generation
        steps.append({
            "step": len(steps) + 1,
            "action": "AI Insight Generation",
            "description": "Generated natural language insights using LLM",
            "details": "Applied domain knowledge and business context",
            "icon": "brain"
        })
        
        # Methodology summary
        methodology = {
            "steps": steps,
            "total_steps": len(steps),
            "operation_type": operation,
            "data_flow": {
                "input_rows": len(original_df),
                "output_rows": len(result_df),
                "reduction_pct": round((1 - len(result_df)/len(original_df)) * 100, 1) if len(original_df) > 0 else 0
            },
            "techniques_used": MethodologyExplainer._get_techniques_used(query_spec)
        }
        
        return methodology
    
    @staticmethod
    def _get_techniques_used(query_spec: dict) -> List[str]:
        """List statistical/analytical techniques used"""
        techniques = []
        
        operation = query_spec.get('operation')
        metrics = query_spec.get('metrics', [])
        
        if operation in ['group_by_single', 'filter_then_group']:
            techniques.append("Group-by aggregation")
        
        if 'failure_rate' in metrics:
            techniques.append("Proportion calculation")
        
        if 'avg_amount' in metrics or 'median_amount' in metrics:
            techniques.append("Central tendency measures")
        
        if 'std_amount' in metrics:
            techniques.append("Dispersion analysis")
        
        if query_spec.get('filter_conditions'):
            techniques.append("Boolean filtering")
        
        techniques.extend([
            "Statistical significance testing",
            "Anomaly detection (IQR & Z-score)",
            "Confidence interval estimation"
        ])
        
        return techniques
    
    @staticmethod
    def explain_metric_calculation(metric_name: str) -> Dict:
        """Explain how a specific metric is calculated"""
        
        explanations = {
            "failure_rate": {
                "name": "Failure Rate",
                "formula": "(Failed Transactions / Total Transactions) × 100",
                "description": "Percentage of transactions that failed",
                "interpretation": "Lower is better. Industry benchmark: 2-5%",
                "example": "If 50 out of 1000 transactions failed, failure rate = 5%"
            },
            "avg_amount": {
                "name": "Average Transaction Amount",
                "formula": "Sum of all amounts / Number of transactions",
                "description": "Mean transaction value in rupees",
                "interpretation": "Indicates typical transaction size",
                "example": "If total is ₹100,000 for 50 transactions, avg = ₹2,000"
            },
            "fraud_rate": {
                "name": "Fraud Flag Rate",
                "formula": "(Flagged Transactions / Total Transactions) × 100",
                "description": "Percentage of transactions flagged for fraud",
                "interpretation": "Higher values indicate more suspicious activity",
                "example": "If 10 out of 1000 are flagged, fraud rate = 1%"
            },
            "median_amount": {
                "name": "Median Transaction Amount",
                "formula": "Middle value when amounts are sorted",
                "description": "50th percentile of transaction amounts",
                "interpretation": "Less affected by outliers than average",
                "example": "For [100, 200, 300, 400, 10000], median = 300"
            },
            "p_value": {
                "name": "P-Value",
                "formula": "Probability of observing this difference by chance",
                "description": "Statistical significance indicator",
                "interpretation": "p < 0.05 means statistically significant",
                "example": "p = 0.03 means 3% chance this is random"
            }
        }
        
        return explanations.get(metric_name, {
            "name": metric_name,
            "description": "Custom metric calculated from data",
            "interpretation": "Refer to documentation for details"
        })
    
    @staticmethod
    def explain_statistical_test(test_type: str, result: dict) -> str:
        """Generate human-readable explanation of statistical test"""
        
        if test_type == "proportion_comparison":
            p_value = result.get('p_value')
            is_sig = result.get('is_significant')
            
            if is_sig:
                explanation = f"The difference is statistically significant (p={p_value}). "
                explanation += "This means the observed difference is unlikely to be due to random chance. "
                explanation += f"We can be 95% confident that the true difference is between "
                explanation += f"{result['confidence_interval']['lower']}% and {result['confidence_interval']['upper']}%."
            else:
                explanation = f"The difference is not statistically significant (p={p_value}). "
                explanation += "This means the observed difference could be due to random variation. "
                explanation += "We cannot confidently conclude that there is a real difference."
            
            return explanation
        
        return "Statistical test completed"
