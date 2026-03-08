"""
Methodology Explainer - Shows step-by-step how insights were generated
"""

from typing import Dict, List


class MethodologyExplainer:
    """Explains the methodology used to generate insights"""
    
    @staticmethod
    def explain_query_execution(query_spec: dict, result_df, original_df) -> Dict:
        """Generate comprehensive step-by-step explanation of query execution"""
        
        steps = []
        calculations = []
        operation = query_spec.get('operation', 'unknown')
        
        # Step 1: Query Understanding
        query_understanding = {
            "intent": MethodologyExplainer._describe_intent(operation),
            "operation": operation,
            "complexity": MethodologyExplainer._assess_complexity(query_spec)
        }
        
        # Step 2: Data Loading
        steps.append(f"📊 Loaded {len(original_df):,} transaction records from dataset ({len(original_df.columns)} columns)")
        
        # Step 3: Filtering
        if query_spec.get('filter_conditions'):
            filters = query_spec['filter_conditions']
            for i, filter_cond in enumerate(filters, 1):
                steps.append(f"🔍 Filter {i}: Applied condition '{filter_cond}'")
                calculations.append(f"df[{filter_cond}]")
            
            rows_after_filter = len(result_df) if operation == 'filter_segment' else "intermediate"
            steps.append(f"✓ Filtering complete: {len(original_df):,} → {rows_after_filter} rows")
        
        # Step 4: Grouping/Aggregation
        if operation in ['group_by_single', 'filter_then_group']:
            group_col = query_spec.get('group_by_column')
            metrics = query_spec.get('metrics', [])
            
            if isinstance(group_col, list):
                steps.append(f"📦 Grouped data by {len(group_col)} columns: {', '.join(group_col)}")
                calculations.append(f"df.groupby({group_col})")
            else:
                steps.append(f"📦 Grouped data by column: '{group_col}'")
                calculations.append(f"df.groupby('{group_col}')")
            
            # Detail each metric calculation
            for metric in metrics:
                metric_desc = MethodologyExplainer._describe_metric(metric)
                steps.append(f"📈 Calculated {metric_desc}")
                calculations.append(MethodologyExplainer._get_metric_formula(metric))
            
            steps.append(f"✓ Created {len(result_df)} groups with {len(metrics)} metrics each")
        
        elif operation == 'top_n_records':
            limit = query_spec.get('limit', 20)
            sort_by = query_spec.get('sort_by', 'unknown')
            ascending = query_spec.get('sort_ascending', False)
            
            steps.append(f"🔢 Sorted data by '{sort_by}' ({'ascending' if ascending else 'descending'})")
            steps.append(f"✂️ Selected top {limit} records")
            calculations.append(f"df.sort_values('{sort_by}', ascending={ascending}).head({limit})")
        
        elif operation == 'filter_segment':
            steps.append(f"✓ Segment analysis complete: {len(result_df):,} records in result")
        
        # Step 5: Statistical Analysis
        steps.append("📊 Performed statistical significance testing:")
        steps.append("  • Calculated confidence intervals (95% level)")
        steps.append("  • Computed p-values for hypothesis testing")
        steps.append("  • Applied anomaly detection (IQR & Z-score methods)")
        
        calculations.append("scipy.stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)")
        calculations.append("scipy.stats.ttest_ind(group1, group2)")
        
        # Step 6: Visualization
        steps.append("📉 Generated interactive visualizations using Apache ECharts")
        
        # Step 7: AI Insight Generation
        steps.append("🤖 Generated natural language insights using AI:")
        steps.append("  • Analyzed patterns and trends")
        steps.append("  • Applied business context and domain knowledge")
        steps.append("  • Generated actionable recommendations")
        
        # Data lineage
        data_lineage = {
            "source_rows": len(original_df),
            "filtered_rows": len(result_df) if operation == 'filter_segment' else len(original_df),
            "result_rows": len(result_df),
            "columns_used": list(query_spec.get('filter_conditions', [])) + [query_spec.get('group_by_column', '')],
            "data_reduction": f"{round((1 - len(result_df)/len(original_df)) * 100, 1)}%"
        }
        
        # Statistical tests applied
        statistical_tests = [
            "Two-sample t-test for comparing group means",
            "Chi-square test for categorical associations",
            "Confidence interval estimation (95% confidence level)",
            "IQR-based outlier detection (Q3 + 1.5×IQR)",
            "Z-score anomaly detection (|z| > 3)",
            "Effect size calculation (Cohen's d)"
        ]
        
        # Techniques used
        techniques_used = MethodologyExplainer._get_techniques_used(query_spec)
        
        # Complete methodology
        methodology = {
            "query_understanding": query_understanding,
            "execution_steps": steps,
            "calculations": calculations,
            "data_lineage": data_lineage,
            "statistical_tests": statistical_tests,
            "techniques_used": techniques_used,
            "operation_type": operation,
            "total_steps": len(steps),
            "data_flow": {
                "input_rows": len(original_df),
                "output_rows": len(result_df),
                "reduction_pct": round((1 - len(result_df)/len(original_df)) * 100, 1) if len(original_df) > 0 else 0
            }
        }
        
        return methodology
    
    @staticmethod
    def _describe_intent(operation: str) -> str:
        """Describe the intent of the operation"""
        intents = {
            "filter_segment": "Filter and analyze a specific segment of data",
            "group_by_single": "Group data and calculate aggregate metrics",
            "filter_then_group": "Filter data first, then group and aggregate",
            "top_n_records": "Find and rank top records by a metric",
            "time_series": "Analyze trends over time",
            "comparison": "Compare metrics across different groups"
        }
        return intents.get(operation, "Analyze data and extract insights")
    
    @staticmethod
    def _assess_complexity(query_spec: dict) -> str:
        """Assess query complexity"""
        score = 0
        
        if query_spec.get('filter_conditions'):
            score += len(query_spec['filter_conditions'])
        
        if query_spec.get('group_by_column'):
            score += 2
        
        if query_spec.get('metrics'):
            score += len(query_spec['metrics'])
        
        if score <= 3:
            return "Simple"
        elif score <= 6:
            return "Medium"
        else:
            return "Complex"
    
    @staticmethod
    def _describe_metric(metric: str) -> str:
        """Describe what a metric calculates"""
        descriptions = {
            "count": "total count of records",
            "failure_rate": "failure rate percentage",
            "fraud_rate": "fraud flag rate percentage",
            "avg_amount": "average transaction amount",
            "median_amount": "median transaction amount",
            "std_amount": "standard deviation of amounts",
            "min_amount": "minimum transaction amount",
            "max_amount": "maximum transaction amount",
            "sum_amount": "total sum of amounts"
        }
        return descriptions.get(metric, metric)
    
    @staticmethod
    def _get_metric_formula(metric: str) -> str:
        """Get the formula/code for a metric"""
        formulas = {
            "count": "len(df)",
            "failure_rate": "(df['transaction_status'] == 'FAILED').sum() / len(df) * 100",
            "fraud_rate": "df['fraud_flag'].sum() / len(df) * 100",
            "avg_amount": "df['amount'].mean()",
            "median_amount": "df['amount'].median()",
            "std_amount": "df['amount'].std()",
            "min_amount": "df['amount'].min()",
            "max_amount": "df['amount'].max()",
            "sum_amount": "df['amount'].sum()"
        }
        return formulas.get(metric, f"calculate_{metric}(df)")
    
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
