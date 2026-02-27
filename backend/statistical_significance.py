"""
Statistical Significance Testing for InsightX Analytics
Provides p-values, confidence intervals, and significance badges
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional


def calculate_proportion_test(success1: int, total1: int, success2: int, total2: int) -> Dict:
    """
    Two-proportion z-test for comparing rates (e.g., failure rates between groups)
    
    Returns:
        dict with p_value, z_score, significant, confidence_interval
    """
    if total1 == 0 or total2 == 0:
        return {
            "p_value": None,
            "z_score": None,
            "significant": False,
            "confidence_level": 0.95,
            "test_type": "two_proportion_z_test",
            "interpretation": "Insufficient data for statistical test"
        }
    
    p1 = success1 / total1
    p2 = success2 / total2
    
    # Pooled proportion
    p_pool = (success1 + success2) / (total1 + total2)
    
    # Standard error
    se = np.sqrt(p_pool * (1 - p_pool) * (1/total1 + 1/total2))
    
    if se == 0:
        return {
            "p_value": 1.0,
            "z_score": 0.0,
            "significant": False,
            "confidence_level": 0.95,
            "test_type": "two_proportion_z_test",
            "interpretation": "No difference detected"
        }
    
    # Z-score
    z_score = (p1 - p2) / se
    
    # Two-tailed p-value
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    # Confidence interval for difference (95%)
    diff = p1 - p2
    ci_margin = 1.96 * se
    ci_lower = diff - ci_margin
    ci_upper = diff + ci_margin
    
    return {
        "p_value": round(p_value, 6),
        "z_score": round(z_score, 3),
        "significant": p_value < 0.05,
        "confidence_level": 0.95,
        "confidence_interval": {
            "lower": round(ci_lower * 100, 2),
            "upper": round(ci_upper * 100, 2),
            "difference_pct": round(diff * 100, 2)
        },
        "test_type": "two_proportion_z_test",
        "interpretation": get_significance_interpretation(p_value, diff * 100)
    }


def calculate_mean_test(values1: np.ndarray, values2: np.ndarray) -> Dict:
    """
    Independent t-test for comparing means (e.g., average amounts between groups)
    """
    if len(values1) < 2 or len(values2) < 2:
        return {
            "p_value": None,
            "t_statistic": None,
            "significant": False,
            "interpretation": "Insufficient data for statistical test"
        }
    
    # Perform t-test
    t_stat, p_value = stats.ttest_ind(values1, values2)
    
    # Calculate confidence interval for difference
    mean_diff = np.mean(values1) - np.mean(values2)
    se_diff = np.sqrt(np.var(values1)/len(values1) + np.var(values2)/len(values2))
    ci_margin = 1.96 * se_diff
    
    return {
        "p_value": round(p_value, 6),
        "t_statistic": round(t_stat, 3),
        "significant": p_value < 0.05,
        "confidence_level": 0.95,
        "confidence_interval": {
            "lower": round(mean_diff - ci_margin, 2),
            "upper": round(mean_diff + ci_margin, 2),
            "mean_difference": round(mean_diff, 2)
        },
        "test_type": "independent_t_test",
        "interpretation": get_significance_interpretation(p_value, mean_diff)
    }


def calculate_chi_square_test(contingency_table: pd.DataFrame) -> Dict:
    """
    Chi-square test for independence (categorical associations)
    """
    if contingency_table.size < 4:
        return {
            "p_value": None,
            "chi_square": None,
            "significant": False,
            "interpretation": "Insufficient data for chi-square test"
        }
    
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    return {
        "p_value": round(p_value, 6),
        "chi_square": round(chi2, 3),
        "degrees_of_freedom": dof,
        "significant": p_value < 0.05,
        "test_type": "chi_square_independence",
        "interpretation": get_significance_interpretation(p_value, chi2)
    }


def get_significance_interpretation(p_value: float, effect_size: float) -> str:
    """Generate human-readable interpretation of statistical test"""
    if p_value is None:
        return "Unable to determine statistical significance"
    
    if p_value < 0.001:
        strength = "extremely strong"
    elif p_value < 0.01:
        strength = "very strong"
    elif p_value < 0.05:
        strength = "strong"
    elif p_value < 0.10:
        strength = "moderate"
    else:
        strength = "weak or no"
    
    if p_value < 0.05:
        return f"Statistically significant difference detected (p={p_value:.4f}). {strength.capitalize()} evidence that this difference is not due to random chance."
    else:
        return f"No statistically significant difference (p={p_value:.4f}). The observed difference could be due to random variation."


def add_significance_to_comparison(df: pd.DataFrame, group_col: str, metric_col: str, 
                                   metric_type: str = "proportion") -> Dict:
    """
    Add statistical significance testing to comparison results
    
    Args:
        df: DataFrame with comparison data
        group_col: Column name for groups being compared
        metric_col: Column name for metric being compared
        metric_type: "proportion" or "mean"
    
    Returns:
        Dict with significance tests for all pairwise comparisons
    """
    if len(df) < 2:
        return {"error": "Need at least 2 groups for comparison"}
    
    results = {
        "pairwise_tests": [],
        "overall_significant": False
    }
    
    # Perform pairwise comparisons
    groups = df[group_col].tolist()
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            group1 = groups[i]
            group2 = groups[j]
            
            if metric_type == "proportion":
                # For rates/proportions (e.g., failure rate)
                total1 = df.iloc[i].get('total_count', 0)
                total2 = df.iloc[j].get('total_count', 0)
                rate1 = df.iloc[i][metric_col]
                rate2 = df.iloc[j][metric_col]
                
                success1 = int(rate1 * total1 / 100)
                success2 = int(rate2 * total2 / 100)
                
                test_result = calculate_proportion_test(success1, total1, success2, total2)
            else:
                # For means (would need raw data, simplified here)
                test_result = {
                    "p_value": None,
                    "significant": False,
                    "interpretation": "Mean comparison requires raw data"
                }
            
            results["pairwise_tests"].append({
                "group1": group1,
                "group2": group2,
                "test_result": test_result
            })
            
            if test_result.get("significant"):
                results["overall_significant"] = True
    
    return results


def calculate_sample_size_adequacy(n: int, effect_size: float = 0.5) -> Dict:
    """
    Determine if sample size is adequate for reliable conclusions
    
    Args:
        n: Sample size
        effect_size: Expected effect size (Cohen's d)
    
    Returns:
        Dict with adequacy assessment
    """
    # Rule of thumb: need at least 30 for normal approximation
    # For effect size 0.5 (medium), need ~64 per group for 80% power
    
    if n < 30:
        adequacy = "low"
        warning = "⚠️ Small sample size (n<30). Results may not be reliable."
        confidence = "Low"
    elif n < 100:
        adequacy = "moderate"
        warning = "Sample size is adequate but larger sample would increase confidence."
        confidence = "Moderate"
    elif n < 1000:
        adequacy = "good"
        warning = None
        confidence = "High"
    else:
        adequacy = "excellent"
        warning = None
        confidence = "Very High"
    
    return {
        "sample_size": n,
        "adequacy": adequacy,
        "confidence": confidence,
        "warning": warning,
        "recommendation": "Collect more data" if n < 100 else "Sample size is sufficient"
    }


def detect_outliers(values: np.ndarray, method: str = "iqr") -> Dict:
    """
    Detect outliers using IQR or Z-score method
    """
    if len(values) < 4:
        return {"outliers": [], "outlier_count": 0, "outlier_pct": 0}
    
    if method == "iqr":
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = values[(values < lower_bound) | (values > upper_bound)]
    else:  # z-score
        z_scores = np.abs(stats.zscore(values))
        outliers = values[z_scores > 3]
    
    return {
        "outliers": outliers.tolist()[:10],  # Show first 10
        "outlier_count": len(outliers),
        "outlier_pct": round(len(outliers) / len(values) * 100, 2),
        "method": method
    }
