"""
Proactive Anomaly Detection for InsightX Analytics
Auto-scans data on load to find unusual patterns
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from scipy import stats


class AnomalyDetector:
    def __init__(self, df: pd.DataFrame, global_stats: Dict):
        self.df = df
        self.global_stats = global_stats
        self.anomalies = []
    
    def detect_all_anomalies(self) -> List[Dict]:
        """Run all anomaly detection checks"""
        self.anomalies = []
        
        # 1. Failure rate anomalies
        self._detect_failure_rate_anomalies()
        
        # 2. Fraud rate anomalies
        self._detect_fraud_rate_anomalies()
        
        # 3. Volume anomalies
        self._detect_volume_anomalies()
        
        # 4. Amount anomalies
        self._detect_amount_anomalies()
        
        # 5. Time-based anomalies
        self._detect_time_anomalies()
        
        # Sort by severity
        self.anomalies.sort(key=lambda x: x['severity_score'], reverse=True)
        
        return self.anomalies[:5]  # Return top 5
    
    def _detect_failure_rate_anomalies(self):
        """Detect segments with unusually high failure rates"""
        baseline_failure_rate = self.global_stats['overall_failure_rate_pct']
        
        # Check by different dimensions
        dimensions = [
            ('is_weekend', 'Weekend vs Weekday'),
            ('transaction_type', 'Transaction Type'),
            ('device_type', 'Device Type'),
            ('network_type', 'Network Type'),
            ('sender_bank', 'Bank')
        ]
        
        for col, label in dimensions:
            if col not in self.df.columns:
                continue
            
            grouped = self.df.groupby(col).agg({
                'transaction_status': lambda x: (x == 'FAILED').mean() * 100,
                'transaction id': 'count'
            }).reset_index()
            
            grouped.columns = [col, 'failure_rate', 'count']
            
            # Find segments with >2x baseline failure rate and >1% of data
            for _, row in grouped.iterrows():
                if row['count'] < len(self.df) * 0.01:  # Skip small segments
                    continue
                
                ratio = row['failure_rate'] / baseline_failure_rate
                
                if ratio > 2.0:  # 2x higher than baseline
                    severity = min(ratio / 2, 5)  # Cap at 5
                    
                    self.anomalies.append({
                        'type': 'high_failure_rate',
                        'severity': 'critical' if ratio > 3 else 'high',
                        'severity_score': severity,
                        'dimension': label,
                        'segment': str(row[col]),
                        'value': round(row['failure_rate'], 2),
                        'baseline': round(baseline_failure_rate, 2),
                        'ratio': round(ratio, 2),
                        'volume_pct': round(row['count'] / len(self.df) * 100, 2),
                        'message': f"⚠️ {label} '{row[col]}' has {ratio:.1f}x higher failure rate ({row['failure_rate']:.1f}% vs {baseline_failure_rate:.1f}% baseline)",
                        'recommendation': f"Investigate {label.lower()} '{row[col]}' - affects {row['count']:,} transactions ({row['count']/len(self.df)*100:.1f}%)"
                    })
    
    def _detect_fraud_rate_anomalies(self):
        """Detect segments with unusually high fraud rates"""
        if 'fraud_flag' not in self.df.columns:
            return
        
        baseline_fraud_rate = self.global_stats['overall_fraud_flag_rate_pct']
        
        dimensions = [
            ('merchant_category', 'Merchant Category'),
            ('sender_age_group', 'Age Group'),
            ('hour_of_day', 'Hour of Day')
        ]
        
        for col, label in dimensions:
            if col not in self.df.columns:
                continue
            
            grouped = self.df.groupby(col).agg({
                'fraud_flag': 'mean',
                'transaction id': 'count'
            }).reset_index()
            
            grouped.columns = [col, 'fraud_rate', 'count']
            grouped['fraud_rate'] *= 100
            
            for _, row in grouped.iterrows():
                if row['count'] < len(self.df) * 0.01:
                    continue
                
                ratio = row['fraud_rate'] / baseline_fraud_rate if baseline_fraud_rate > 0 else 0
                
                if ratio > 2.5:
                    severity = min(ratio / 2, 5)
                    
                    self.anomalies.append({
                        'type': 'high_fraud_rate',
                        'severity': 'critical' if ratio > 4 else 'high',
                        'severity_score': severity,
                        'dimension': label,
                        'segment': str(row[col]),
                        'value': round(row['fraud_rate'], 2),
                        'baseline': round(baseline_fraud_rate, 2),
                        'ratio': round(ratio, 2),
                        'volume_pct': round(row['count'] / len(self.df) * 100, 2),
                        'message': f"🚨 {label} '{row[col]}' has {ratio:.1f}x higher fraud rate ({row['fraud_rate']:.1f}% vs {baseline_fraud_rate:.1f}% baseline)",
                        'recommendation': f"Flag {label.lower()} '{row[col]}' for fraud investigation"
                    })
    
    def _detect_volume_anomalies(self):
        """Detect unusual transaction volume patterns"""
        if 'hour_of_day' not in self.df.columns:
            return
        
        hourly_counts = self.df.groupby('hour_of_day').size()
        mean_hourly = hourly_counts.mean()
        std_hourly = hourly_counts.std()
        
        for hour, count in hourly_counts.items():
            z_score = (count - mean_hourly) / std_hourly if std_hourly > 0 else 0
            
            if abs(z_score) > 2.5:  # More than 2.5 std deviations
                anomaly_type = 'volume_spike' if z_score > 0 else 'volume_drop'
                
                self.anomalies.append({
                    'type': anomaly_type,
                    'severity': 'medium',
                    'severity_score': abs(z_score) / 2,
                    'dimension': 'Hour of Day',
                    'segment': f'{hour:02d}:00',
                    'value': int(count),
                    'baseline': int(mean_hourly),
                    'z_score': round(z_score, 2),
                    'message': f"📊 Hour {hour:02d}:00 shows {'unusually high' if z_score > 0 else 'unusually low'} volume ({count:,} vs {mean_hourly:,.0f} average)",
                    'recommendation': f"{'Peak capacity planning' if z_score > 0 else 'Investigate low activity'} for hour {hour:02d}:00"
                })
    
    def _detect_amount_anomalies(self):
        """Detect unusual transaction amounts"""
        amount_col = None
        for col in self.df.columns:
            if 'amount' in col.lower():
                amount_col = col
                break
        
        if not amount_col:
            return
        
        amounts = self.df[amount_col].dropna()
        
        # Detect outliers using IQR method
        q1 = amounts.quantile(0.25)
        q3 = amounts.quantile(0.75)
        iqr = q3 - q1
        upper_bound = q3 + 3 * iqr  # 3x IQR for extreme outliers
        
        outliers = amounts[amounts > upper_bound]
        
        if len(outliers) > 0:
            outlier_pct = len(outliers) / len(amounts) * 100
            
            if outlier_pct > 0.5:  # More than 0.5% are outliers
                self.anomalies.append({
                    'type': 'amount_outliers',
                    'severity': 'medium',
                    'severity_score': min(outlier_pct, 3),
                    'dimension': 'Transaction Amount',
                    'segment': 'High-value outliers',
                    'value': len(outliers),
                    'outlier_pct': round(outlier_pct, 2),
                    'threshold': round(upper_bound, 2),
                    'max_amount': round(outliers.max(), 2),
                    'message': f"💰 {len(outliers):,} transactions ({outlier_pct:.2f}%) exceed ₹{upper_bound:,.0f} (3x IQR threshold)",
                    'recommendation': f"Review high-value transactions above ₹{upper_bound:,.0f} for fraud risk"
                })
    
    def _detect_time_anomalies(self):
        """Detect unusual patterns by time of day/week"""
        if 'is_weekend' not in self.df.columns or 'transaction_status' not in self.df.columns:
            return
        
        # Weekend vs weekday failure rate
        weekend_failures = self.df[self.df['is_weekend'] == 1]['transaction_status'].apply(lambda x: x == 'FAILED').mean() * 100
        weekday_failures = self.df[self.df['is_weekend'] == 0]['transaction_status'].apply(lambda x: x == 'FAILED').mean() * 100
        
        if weekend_failures > 0 and weekday_failures > 0:
            ratio = weekend_failures / weekday_failures
            
            if ratio > 1.5 or ratio < 0.67:  # 50% difference
                self.anomalies.append({
                    'type': 'time_pattern',
                    'severity': 'medium',
                    'severity_score': abs(ratio - 1) * 2,
                    'dimension': 'Weekend vs Weekday',
                    'segment': 'Weekend' if ratio > 1 else 'Weekday',
                    'value': round(weekend_failures if ratio > 1 else weekday_failures, 2),
                    'baseline': round(weekday_failures if ratio > 1 else weekend_failures, 2),
                    'ratio': round(ratio if ratio > 1 else 1/ratio, 2),
                    'message': f"📅 {'Weekend' if ratio > 1 else 'Weekday'} failure rate is {ratio if ratio > 1 else 1/ratio:.1f}x {'higher' if ratio > 1 else 'lower'} ({weekend_failures:.1f}% vs {weekday_failures:.1f}%)",
                    'recommendation': f"Optimize {'weekend' if ratio > 1 else 'weekday'} operations to reduce failures"
                })


def scan_for_anomalies(df: pd.DataFrame, global_stats: Dict) -> List[Dict]:
    """
    Main function to scan dataset for anomalies
    
    Returns:
        List of anomaly dictionaries sorted by severity
    """
    detector = AnomalyDetector(df, global_stats)
    return detector.detect_all_anomalies()
