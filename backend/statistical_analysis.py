"""
Statistical Analysis Module for InsightX
Provides statistical significance testing, confidence intervals, and anomaly detection
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional


class StatisticalAnalyzer:
    """Performs statistical analysis on transaction data"""
    
    def __init__(self, df: pd.DataFrame, global_stats: dict):
        self.df = df
        self.global_stats = global_stats
    
    def compare_proportions(self, group1_success: int, group1_total: int, 
                           group2_success: int, group2_total: int) -> Dict:
        """
        Compare two proportions (e.g., success rates) with statistical significance
        
        Returns:
            dict with p_value, is_significant, confidence_interval, effect_size
        """
        if group1_total == 0 or group2_total == 0:
            return {
                "p_value": None,
                "is_significant": False,
                "confidence_level": 0.95,
                "effect_size": None,
                "interpretation": "Insufficient data for statistical test"
            }
        
        # Calculate proportions
        p1 = group1_success / group1_total
        p2 = group2_success / group2_total
        
        # Pooled proportion
        p_pool = (group1_success + group2_success) / (group1_total + group2_total)
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/group1_total + 1/group2_total))
        
        # Z-score
        if se == 0:
            z_score = 0
            p_value = 1.0
        else:
            z_score = (p1 - p2) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))  # Two-tailed test
        
        # Effect size (Cohen's h)
        effect_size = 2 * (np.arcsin(np.sqrt(p1)) - np.arcsin(np.sqrt(p2)))
        
        # Confidence interval for difference
        se_diff = np.sqrt(p1*(1-p1)/group1_total + p2*(1-p2)/group2_total)
        ci_lower = (p1 - p2) - 1.96 * se_diff
        ci_upper = (p1 - p2) + 1.96 * se_diff
        
        # Interpretation
        is_significant = p_value < 0.05
        
        if is_significant:
            if abs(effect_size) < 0.2:
                effect_desc = "small but significant"
            elif abs(effect_size) < 0.5:
                effect_desc = "moderate and significant"
            else:
                effect_desc = "large and highly significant"
        else:
            effect_desc = "not statistically significant"
        
        return {
            "p_value": round(p_value, 4),
            "is_significant": is_significant,
            "confidence_level": 0.95,
            "confidence_interval": {
                "lower": round(ci_lower * 100, 2),
                "upper": round(ci_upper * 100, 2),
                "difference_pct": round((p1 - p2) * 100, 2)
            },
            "effect_size": round(effect_size, 3),
            "effect_description": effect_desc,
            "interpretation": f"The difference is {effect_desc} (p={p_value:.4f})",
            "sample_sizes": {
                "group1": group1_total,
                "group2": group2_total
            }
        }
    
    def detect_anomalies(self, result_df: pd.DataFrame, metric_col: str) -> List[Dict]:
        """
        Detect anomalies in a metric using IQR method and Z-score
        
        Returns:
            List of anomaly dictionaries with details
        """
        if metric_col not in result_df.columns:
            return []
        
        values = result_df[metric_col].dropna()
        if len(values) < 3:
            return []
        
        anomalies = []
        
        # IQR method
        Q1 = values.quantile(0.25)
        Q3 = values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Z-score method
        mean = values.mean()
        std = values.std()
        
        for idx, row in result_df.iterrows():
            value = row[metric_col]
            if pd.isna(value):
                continue
            
            # Check IQR outlier
            is_iqr_outlier = value < lower_bound or value > upper_bound
            
            # Check Z-score outlier (|z| > 2.5)
            z_score = (value - mean) / std if std > 0 else 0
            is_zscore_outlier = abs(z_score) > 2.5
            
            if is_iqr_outlier or is_zscore_outlier:
                # Get category name (first column)
                category = row[result_df.columns[0]]
                
                # Calculate how extreme
                if value > upper_bound:
                    deviation_pct = ((value - mean) / mean) * 100
                    direction = "higher"
                else:
                    deviation_pct = ((mean - value) / mean) * 100
                    direction = "lower"
                
                anomalies.append({
                    "category": str(category),
                    "value": round(value, 2),
                    "mean": round(mean, 2),
                    "deviation_pct": round(abs(deviation_pct), 1),
                    "direction": direction,
                    "z_score": round(z_score, 2),
                    "severity": "high" if abs(z_score) > 3 else "medium",
                    "message": f"{category} is {abs(deviation_pct):.1f}% {direction} than average"
                })
        
        # Sort by severity
        anomalies.sort(key=lambda x: abs(x['z_score']), reverse=True)
        return anomalies[:5]  # Return top 5 anomalies
    
    def calculate_confidence_interval(self, values: pd.Series, confidence: float = 0.95) -> Dict:
        """
        Calculate confidence interval for a metric
        """
        if len(values) < 2:
            return None
        
        mean = values.mean()
        std_err = stats.sem(values)
        ci = stats.t.interval(confidence, len(values)-1, loc=mean, scale=std_err)
        
        return {
            "mean": round(mean, 2),
            "confidence_level": confidence,
            "lower_bound": round(ci[0], 2),
            "upper_bound": round(ci[1], 2),
            "margin_of_error": round((ci[1] - ci[0]) / 2, 2)
        }
    
    def compare_groups_statistical(self, result_df: pd.DataFrame, 
                                   group_col: str, metric_col: str) -> Dict:
        """
        Perform statistical comparison between groups
        """
        if len(result_df) < 2:
            return None
        
        # Get top 2 groups for comparison
        top_groups = result_df.nlargest(2, metric_col)
        
        if len(top_groups) < 2:
            return None
        
        group1 = top_groups.iloc[0]
        group2 = top_groups.iloc[1]
        
        # For failure rates, we need success/total counts
        # Approximate from the data
        if 'total_count' in result_df.columns:
            group1_total = int(group1['total_count'])
            group2_total = int(group2['total_count'])
            
            # If metric is a rate (percentage)
            if 'rate' in metric_col.lower() or 'pct' in metric_col.lower():
                group1_success = int(group1_total * (group1[metric_col] / 100))
                group2_success = int(group2_total * (group2[metric_col] / 100))
                
                stats_result = self.compare_proportions(
                    group1_success, group1_total,
                    group2_success, group2_total
                )
                
                stats_result['group1_name'] = str(group1[group_col])
                stats_result['group2_name'] = str(group2[group_col])
                stats_result['group1_value'] = round(group1[metric_col], 2)
                stats_result['group2_value'] = round(group2[metric_col], 2)
                
                return stats_result
        
        return None
    
    def get_data_quality_score(self, result_df: pd.DataFrame) -> Dict:
        """
        Calculate data quality indicators
        """
        total_rows = len(self.df)
        result_rows = len(result_df)
        
        # Sample size adequacy
        sample_pct = (result_rows / total_rows) * 100
        
        if sample_pct >= 10:
            adequacy = "Excellent"
            confidence = "High"
        elif sample_pct >= 5:
            adequacy = "Good"
            confidence = "High"
        elif sample_pct >= 1:
            adequacy = "Adequate"
            confidence = "Medium"
        else:
            adequacy = "Limited"
            confidence = "Low"
        
        # Check for missing values
        missing_pct = (result_df.isnull().sum().sum() / (len(result_df) * len(result_df.columns))) * 100
        
        return {
            "sample_size": result_rows,
            "sample_percentage": round(sample_pct, 2),
            "total_population": total_rows,
            "adequacy": adequacy,
            "confidence": confidence,
            "missing_data_pct": round(missing_pct, 2),
            "completeness": round(100 - missing_pct, 1),
            "recommendation": self._get_sample_recommendation(sample_pct, result_rows)
        }
    
    def _get_sample_recommendation(self, sample_pct: float, sample_size: int) -> str:
        """Get recommendation based on sample size"""
        if sample_size < 30:
            return "Small sample size - results may not be generalizable"
        elif sample_pct < 1:
            return "Limited sample - consider broader filters for more robust insights"
        elif sample_pct < 5:
            return "Adequate sample - results are reasonably reliable"
        else:
            return "Large sample - results are highly reliable"


def add_statistical_analysis(result_df: pd.DataFrame, query_spec: dict, 
                            df: pd.DataFrame, global_stats: dict) -> Dict:
    """
    Add statistical analysis to query results
    
    Returns:
        Dictionary with statistical insights
    """
    analyzer = StatisticalAnalyzer(df, global_stats)
    
    statistical_insights = {
        "data_quality": analyzer.get_data_quality_score(result_df),
        "anomalies": [],
        "statistical_comparison": None,
        "confidence_intervals": {}
    }
    
    # Detect anomalies in numeric columns
    for col in result_df.columns:
        if result_df[col].dtype in ['float64', 'int64'] and col != result_df.columns[0]:
            anomalies = analyzer.detect_anomalies(result_df, col)
            if anomalies:
                statistical_insights["anomalies"].extend(anomalies)
    
    # Statistical comparison for grouped data
    if query_spec.get('operation') in ['group_by_single', 'filter_then_group']:
        group_col = result_df.columns[0]
        
        # Find metric column (failure_rate, avg_amount, etc.)
        for col in result_df.columns[1:]:
            if 'rate' in col.lower() or 'pct' in col.lower():
                comparison = analyzer.compare_groups_statistical(result_df, group_col, col)
                if comparison:
                    statistical_insights["statistical_comparison"] = comparison
                break
    
    # Confidence intervals for numeric metrics
    for col in result_df.columns:
        if result_df[col].dtype in ['float64', 'int64'] and len(result_df) >= 2:
            ci = analyzer.calculate_confidence_interval(result_df[col])
            if ci:
                statistical_insights["confidence_intervals"][col] = ci
    
    return statistical_insights
