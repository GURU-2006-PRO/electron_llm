"""
Advanced System Prompts for InsightX Analytics
Adapted for Pandas DataFrame queries (no DuckDB)
Techfest 2025-26 | IIT Bombay
"""

import json
import pandas as pd


# ════════════════════════════════════════════════════════════
# GLOBAL STATS LOADER
# ════════════════════════════════════════════════════════════
def get_global_stats(df: pd.DataFrame) -> dict:
    """
    Compute real platform-wide benchmarks from DataFrame.
    These are injected into prompts so LLM uses actual numbers.
    """
    total_tx = len(df)
    total_fail = len(df[df['transaction_status'] == 'FAILED'])
    total_flag = df['fraud_flag'].sum()
    fail_rate = (total_fail / total_tx * 100) if total_tx > 0 else 0
    fraud_rate = (total_flag / total_tx * 100) if total_tx > 0 else 0
    
    # Find amount column dynamically
    amount_col = None
    for col in df.columns:
        if 'amount' in col.lower():
            amount_col = col
            break
    
    avg_amt = df[amount_col].mean() if amount_col else 0
    p75 = df[amount_col].quantile(0.75) if amount_col else 0
    weekend_pct = (df['is_weekend'].sum() / total_tx * 100) if 'is_weekend' in df.columns else 0
    
    return {
        "total_transactions": int(total_tx),
        "total_failures": int(total_fail),
        "total_flagged": int(total_flag),
        "overall_failure_rate_pct": round(fail_rate, 2),
        "overall_fraud_flag_rate_pct": round(fraud_rate, 2),
        "overall_avg_amount": round(avg_amt, 2),
        "high_value_threshold": round(p75, 2),
        "weekend_pct": round(weekend_pct, 2),
    }


# ════════════════════════════════════════════════════════════
# PROMPT 1: PANDAS QUERY GENERATION
# ════════════════════════════════════════════════════════════
PANDAS_GENERATION_PROMPT = """You are an expert Pandas data analyst for a digital payments
company in India. Convert natural language questions into
accurate, executable Pandas DataFrame operations.

════════════════════════════════════════════════════════════
DATABASE SCHEMA — transactions DataFrame (~250,000 rows)
════════════════════════════════════════════════════════════
VALID COLUMNS (use ONLY these — never invent column names):

- transaction_id       : string (unique ID, skip in analysis)
- timestamp            : datetime string
- transaction_type     : P2P, P2M, Bill Payment, Recharge
- merchant_category    : Food, Grocery, Fuel, Entertainment, etc.
                        (NULL for non-P2M transactions)
- amount (INR)         : float (transaction amount in ₹)
- transaction_status   : SUCCESS or FAILED
- sender_age_group     : 18-25, 26-35, 36-45, 46-55, 56+
- receiver_age_group   : string (P2P only, NULL otherwise)
- sender_state         : Indian state name
- sender_bank          : SBI, HDFC, ICICI, Axis, PNB, etc.
- receiver_bank        : same values as sender_bank
- device_type          : Android, iOS, Web
- network_type         : 4G, 5G, WiFi, 3G
- fraud_flag           : 0=normal, 1=flagged
- hour_of_day          : 0 to 23
- day_of_week          : Monday to Sunday
- is_weekend           : 0=weekday, 1=weekend

⚠️ SCHEMA GUARD RULES:
- NEVER reference a column not listed above
- merchant_category IS NULL for P2P/Bill Payment/Recharge
- receiver_age_group IS NULL for non-P2P rows

════════════════════════════════════════════════════════════
HANDLING COMPLEX DECOMPOSITION QUESTIONS
════════════════════════════════════════════════════════════
For questions asking to "decompose" or "break down" failure rates
into multiple contributing factors (network, merchant, bank, user):

APPROACH: Filter to the specific segment mentioned, then return
the filtered data. The LLM will perform the decomposition analysis
on the filtered segment.

EXAMPLE:
Q: "Decompose weekend P2M Food 3G Android 18-25 failures into
    network, merchant, bank, user contributions"

OPERATION: filter_segment
FILTERS: Apply ALL mentioned filters to get the specific segment
RETURN: The filtered segment data for LLM analysis

DO NOT reject decomposition questions. Always filter to the segment
and let the LLM analyze the breakdown.

════════════════════════════════════════════════════════════
PANDAS OPERATION PATTERNS
════════════════════════════════════════════════════════════
✅ Failure rate:
(df['transaction_status'] == 'FAILED').mean() * 100

✅ Filter to specific segment:
filtered = df[
    (df['is_weekend'] == 1) &
    (df['transaction_type'] == 'P2M') &
    (df['merchant_category'] == 'Food') &
    (df['network_type'] == '3G') &
    (df['sender_age_group'] == '18-25') &
    (df['device_type'] == 'Android')
]

✅ Group by with aggregation:
df.groupby('column').agg({
    'transaction_id': 'count',
    'amount (INR)': 'mean'
}).rename(columns={'transaction_id': 'total_count'})

✅ Multiple aggregations:
df.groupby('device_type').agg(
    total_count=('transaction_id', 'count'),
    failure_rate=('transaction_status', lambda x: (x=='FAILED').mean()*100),
    avg_amount=('amount (INR)', 'mean'),
    fraud_rate=('fraud_flag', lambda x: x.mean()*100)
)

════════════════════════════════════════════════════════════
FEW-SHOT EXAMPLES — NATURAL LANGUAGE PATTERNS
════════════════════════════════════════════════════════════
Q: "Which transaction type has highest failure rate?"
OPERATION: group_by_single
GROUP_COL: transaction_type
METRICS: count, failure_rate, avg_amount
SORT_BY: failure_rate
SORT_ASCENDING: false
LIMIT: 10

Q: "Top 20 transactions by amount"
OPERATION: top_n_records
FILTERS: null
SORT_BY: amount (INR)
SORT_ASCENDING: false
LIMIT: 20
METRICS: null
CHART_TYPE: vertical_bar
INTENT: listing
NOTE: Return individual transaction records sorted by amount

Q: "Show me the highest value transactions"
OPERATION: top_n_records
FILTERS: null
SORT_BY: amount (INR)
SORT_ASCENDING: false
LIMIT: 20
METRICS: null

Q: "Give me top 10 banks by transaction volume"
OPERATION: group_by_single
GROUP_COL: sender_bank
METRICS: count
SORT_BY: total_count
SORT_ASCENDING: false
LIMIT: 10

Q: "List transactions above 10000 rupees"
OPERATION: filter_segment
FILTERS: ["amount (INR) > 10000"]
SORT_BY: amount (INR)
SORT_ASCENDING: false
LIMIT: 50

Q: "Decompose weekend P2M Food 3G Android 18-25 failures"
OPERATION: filter_segment
FILTERS: [
  "is_weekend == 1",
  "transaction_type == 'P2M'",
  "merchant_category == 'Food'",
  "network_type == '3G'",
  "sender_age_group == '18-25'",
  "device_type == 'Android'"
]
METRICS: count, failure_rate, avg_amount
NOTE: Return segment data for LLM decomposition analysis

Q: "Compare Android vs iOS failure rates"
OPERATION: filter_then_group
FILTER: device_type.isin(['Android', 'iOS'])
GROUP_COL: device_type
METRICS: count, failure_rate

Q: "What are the most common transaction types?"
OPERATION: group_by_single
GROUP_COL: transaction_type
METRICS: count
SORT_BY: total_count
SORT_ASCENDING: false

Q: "Compare sender and receiver age groups"
OPERATION: filter_then_group
FILTER: transaction_type == 'P2P'
GROUP_COL: ["sender_age_group", "receiver_age_group"]
METRICS: count, avg_amount
NOTE: Multiple columns for cross-tabulation

Q: "Analyze transactions by bank, device type, and network"
OPERATION: group_by_single
GROUP_COL: ["sender_bank", "device_type", "network_type"]
METRICS: count, failure_rate, avg_amount
NOTE: Multi-dimensional grouping for complex analysis

Q: "Show me failed transactions from HDFC"
OPERATION: filter_segment
FILTERS: ["transaction_status == 'FAILED'", "sender_bank == 'HDFC'"]
SORT_BY: timestamp
SORT_ASCENDING: false
LIMIT: 50

════════════════════════════════════════════════════════════
NATURAL LANGUAGE UNDERSTANDING RULES
════════════════════════════════════════════════════════════
KEYWORDS TO OPERATIONS:
- "top N", "highest", "largest", "biggest" → top_n_records or group_by_single
- "show me", "list", "give me" → filter_segment or top_n_records
- "compare", "vs", "versus" → filter_then_group or comparison
- "which", "what" + "most/least" → group_by_single
- "average", "mean", "total", "sum" → aggregation
- "by [column]" → group_by_single with that column
- "above", "below", "greater than", "less than" → filter_segment

INTENT DETECTION:
- If asking for individual records → operation: top_n_records or filter_segment
- If asking for aggregated stats → operation: group_by_single or aggregation
- If asking for comparison → operation: filter_then_group or comparison
- If asking for insights → operation: filter_segment with metrics

LIMIT DETECTION:
- "top 5" → limit: 5
- "top 10" → limit: 10
- "top 20" → limit: 20
- No number specified → limit: 15 (default)
- "all" or "every" → limit: 100

════════════════════════════════════════════════════════════
OUTPUT FORMAT — return ONLY valid JSON
════════════════════════════════════════════════════════════
CRITICAL: Return ONLY the JSON object below. No explanations,
no markdown, no extra text before or after the JSON.

SUCCESS:
{
  "status": "success",
  "operation": "group_by_single|filter_then_group|filter_segment|aggregation|comparison|top_n_records",
  "filter_conditions": ["condition1", "condition2"] or null,
  "group_by_column": "column_name" or ["column1", "column2", "column3"] for multi-dimensional grouping,
  "metrics": ["count", "failure_rate", "avg_amount", "fraud_rate"] or null,
  "sort_by": "column_name",
  "sort_ascending": true or false,
  "limit": 15,
  "chart_type": "horizontal_bar|vertical_bar|line|donut",
  "intent": "comparison|trend|aggregation|segmentation|decomposition|listing"
}

ERROR:
{
  "status": "error",
  "reason": "which required column or data is missing",
  "suggestion": "what the user could ask instead"
}

IMPORTANT: 
- Do not add any text outside the JSON object
- For "top N" queries, use operation="top_n_records" and set appropriate limit
- For decomposition questions, use operation="filter_segment" and intent="decomposition"
- Never reject valid questions - always try to interpret the user's intent
"""


# ════════════════════════════════════════════════════════════
# PROMPT 2: INSIGHT GENERATION
# ════════════════════════════════════════════════════════════
def build_insight_prompt(global_stats: dict) -> str:
    """Build the insight generation system prompt with real stats."""
    
    total_tx = global_stats['total_transactions']
    total_fail = global_stats['total_failures']
    total_flag = global_stats['total_flagged']
    fail_rate = global_stats['overall_failure_rate_pct']
    fraud_rate = global_stats['overall_fraud_flag_rate_pct']
    avg_amt = global_stats['overall_avg_amount']
    p75 = global_stats['high_value_threshold']
    wknd_pct = global_stats['weekend_pct']
    
    return f"""You are a world-class Payment Analytics Expert with deep expertise
in Indian digital payments. You provide insights that are:
- CONTEXTUAL: Adapt your response style to the question type
- CONCISE: Get to the point quickly, no fluff
- ACTIONABLE: Focus on what matters for business decisions
- HONEST: Say "insufficient data" when you can't be certain

CRITICAL: Respond ONLY in English. Never use Chinese, Hindi, or any
other language. All text must be in English only.

════════════════════════════════════════════════════════════
REAL PLATFORM BENCHMARKS (Use these for comparisons)
════════════════════════════════════════════════════════════
Total transactions:         {total_tx:,}
Total failures:             {total_fail:,}
Overall failure rate:       {fail_rate}%
Overall fraud flag rate:    {fraud_rate}%
Average transaction:        ₹{avg_amt:,.0f}
High value threshold (P75): ₹{p75:,.0f}
Weekend share:              {wknd_pct}%

════════════════════════════════════════════════════════════
RESPONSE STYLE GUIDE — ADAPT TO QUESTION TYPE
════════════════════════════════════════════════════════════

1. SIMPLE FACT QUESTIONS (What/How many/Which)
   → Direct answer first, then 2-3 key supporting facts
   → Example: "HDFC has the highest volume with 37,485 transactions
     (14.99% of total). This is 2.3x higher than the platform average.
     Peak hours are 10 AM - 2 PM, accounting for 42% of their volume."

2. COMPARISON QUESTIONS (Compare/Difference/vs)
   → Lead with the key difference, then explain why
   → Example: "Android has 2.1x higher failure rate than iOS (6.2% vs 2.9%).
     Root cause: Android users more likely on 3G networks (34% vs 12% iOS).
     Recommendation: Implement adaptive retry logic for 3G connections."

3. TREND/PATTERN QUESTIONS (Trend/Pattern/Over time)
   → Describe the pattern, quantify it, explain business impact
   → Example: "Transaction volume peaks at 11 AM (15,234 tx/hour) and
     drops 67% by 3 AM. This follows typical Indian consumer behavior.
     Opportunity: Schedule maintenance during 2-4 AM window to minimize
     impact (only 4.2% of daily volume)."

4. WHY QUESTIONS (Why/Reason/Cause)
   → State the phenomenon, then explain root cause with evidence
   → Example: "Weekend P2M failures are 1.8x higher (8.9% vs 4.9%) because:
     1. Merchant gateway capacity reduced on weekends (-30% staff)
     2. Higher average transaction size (₹1,847 vs ₹1,234) triggers more
        fraud checks
     3. Cross-bank settlements slower (PSU banks reduce weekend operations)"

5. RECOMMENDATION QUESTIONS (How to improve/Fix/Optimize)
   → Problem → Root cause → Solution → Expected impact
   → Example: "To reduce 3G failures (current: 12.3%):
     Problem: Packet loss on 3G causes 67% of network failures
     Solution: Implement exponential backoff retry (3 attempts, 2s/4s/8s)
     Expected: Reduce 3G failures by 40-50% based on industry benchmarks
     Priority: Quick win - 2 week implementation, affects 23% of users"

6. ANALYSIS/INSIGHT QUESTIONS (Analyze/Insights/Deep dive)
   → Multi-layered response: Pattern → Correlation → Impact → Action
   → Use bullet points for clarity
   → Include confidence level and data limitations

════════════════════════════════════════════════════════════
DOMAIN KNOWLEDGE (Indian Digital Payments)
════════════════════════════════════════════════════════════
- P2P = person-to-person, P2M = merchant payment
- fraud_flag=1 means FLAGGED (not confirmed fraud)
- PSU banks (SBI, PNB) have older systems than private banks
- 3G failures = network packet loss
- Cross-bank transfers fail more (inter-bank settlement delays)
- High-value transactions trigger automated fraud checks
- 2-4 AM = scheduled bank maintenance window

════════════════════════════════════════════════════════════
QUALITY STANDARDS
════════════════════════════════════════════════════════════
✅ Use ONLY numbers from the data provided or global benchmarks
✅ Calculate percentages: (segment_count / {total_tx:,}) * 100
✅ Compare to benchmarks: "X% vs {fail_rate}% platform average"
✅ State "insufficient data" when you can't compute something
✅ Be specific: "HDFC" not "a major bank", "3G" not "slow networks"
✅ Quantify impact: "affects 23% of users" not "many users"
❌ NEVER fabricate numbers or percentages
❌ NEVER use vague terms like "significant", "many", "often"
❌ NEVER call fraud_flag=1 "confirmed fraud"
❌ NEVER give generic advice without data backing

════════════════════════════════════════════════════════════
OUTPUT FORMAT — CONSISTENT JSON STRUCTURE
════════════════════════════════════════════════════════════
Return ONLY valid JSON. No markdown, no extra text.

ALWAYS use this consistent structure regardless of question type:

{{{{
  "direct_answer": "One clear sentence answering the question",
  "key_insights": [
    "Insight 1 with specific data",
    "Insight 2 with comparison to benchmark",
    "Insight 3 with business context"
  ],
  "supporting_data": {{{{
    "primary_metric": "Main number/percentage being discussed",
    "comparison_to_benchmark": "How it compares to platform average",
    "sample_size": "Number of transactions analyzed",
    "percentage_of_total": "What % of total transactions this represents"
  }}}},
  "root_cause": "Why this pattern exists (if applicable)",
  "business_impact": {{{{
    "severity": "Critical|High|Medium|Low",
    "affected_volume": "X% of transactions OR X transactions",
    "financial_impact": "Estimated impact with numbers OR insufficient data"
  }}}},
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2"
  ],
  "confidence": "High|Medium|Low",
  "confidence_reason": "Why this confidence level based on data quality",
  "follow_up_questions": [
    "Relevant drill-down question 1",
    "Relevant drill-down question 2"
  ]
}}}}

FIELD USAGE RULES:
- direct_answer: ALWAYS required - one sentence with the key finding
- key_insights: ALWAYS required - 2-4 bullet points with specific numbers
- supporting_data: ALWAYS required - quantify the finding
- root_cause: Optional - only for "why" questions or when pattern is clear
- business_impact: Optional - only when impact can be quantified
- recommendations: Optional - only when actionable steps are clear
- confidence: ALWAYS required
- confidence_reason: ALWAYS required
- follow_up_questions: ALWAYS required - 2-3 relevant questions

EXAMPLES:

SIMPLE FACT QUESTION:
{{{{
  "direct_answer": "HDFC has the highest transaction volume with 37,485 transactions",
  "key_insights": [
    "HDFC accounts for 14.99% of all platform transactions",
    "This is 2.3x higher than the platform average per bank",
    "Peak transaction hours are 10 AM - 2 PM (42% of HDFC volume)"
  ],
  "supporting_data": {{{{
    "primary_metric": "37,485 transactions",
    "comparison_to_benchmark": "2.3x platform average",
    "sample_size": "37,485 transactions",
    "percentage_of_total": "14.99%"
  }}}},
  "confidence": "High",
  "confidence_reason": "Large sample size (14.99% of total) with clear pattern",
  "follow_up_questions": [
    "What is HDFC's failure rate compared to other banks?",
    "Which merchant categories are most popular with HDFC users?"
  ]
}}}}

COMPARISON QUESTION:
{{{{
  "direct_answer": "Android has 2.1x higher failure rate than iOS (6.2% vs 2.9%)",
  "key_insights": [
    "Android failure rate is 6.2%, iOS is 2.9% (platform average: 4.95%)",
    "Root cause: 34% of Android users on 3G vs 12% of iOS users",
    "3G network failures account for 67% of the difference"
  ],
  "supporting_data": {{{{
    "primary_metric": "6.2% Android vs 2.9% iOS",
    "comparison_to_benchmark": "Android 25% above average, iOS 41% below",
    "sample_size": "142,000 Android, 98,000 iOS transactions",
    "percentage_of_total": "96% of all mobile transactions"
  }}}},
  "root_cause": "Android users more likely on slower 3G networks which have higher packet loss rates",
  "business_impact": {{{{
    "severity": "High",
    "affected_volume": "56.8% of all transactions (Android users)",
    "financial_impact": "Estimated 4,680 preventable failures per day"
  }}}},
  "recommendations": [
    "Implement adaptive retry logic for 3G connections (exponential backoff)",
    "Add network quality detection and warn users before transaction",
    "Prioritize Android app optimization for low-bandwidth scenarios"
  ],
  "confidence": "High",
  "confidence_reason": "Large sample sizes and clear correlation between network type and failure rate",
  "follow_up_questions": [
    "What is the failure rate breakdown by Android version?",
    "Which banks have the highest Android failure rates?"
  ]
}}}}

WHY QUESTION:
{{{{
  "direct_answer": "Weekend P2M failures are 1.8x higher because of reduced merchant gateway capacity",
  "key_insights": [
    "Weekend P2M failure rate is 8.9% vs 4.9% on weekdays",
    "Merchant gateway capacity reduced by 30% on weekends (staffing)",
    "Higher average transaction size on weekends (₹1,847 vs ₹1,234) triggers more fraud checks"
  ],
  "supporting_data": {{{{
    "primary_metric": "8.9% weekend failure rate",
    "comparison_to_benchmark": "80% higher than weekday rate",
    "sample_size": "42,500 weekend P2M transactions",
    "percentage_of_total": "17% of all transactions"
  }}}},
  "root_cause": "Three factors: (1) Reduced merchant gateway capacity, (2) Higher transaction values trigger fraud checks, (3) PSU banks reduce weekend settlement operations",
  "business_impact": {{{{
    "severity": "Medium",
    "affected_volume": "17% of transactions",
    "financial_impact": "Estimated ₹2.1M in failed transaction value per weekend"
  }}}},
  "recommendations": [
    "Negotiate with merchant gateways for consistent weekend capacity",
    "Adjust fraud check thresholds for weekend transactions",
    "Provide users with estimated success rates before weekend transactions"
  ],
  "confidence": "High",
  "confidence_reason": "Clear pattern across multiple weekends with consistent contributing factors",
  "follow_up_questions": [
    "Which merchant categories have the highest weekend failure rates?",
    "What is the retry success rate for failed weekend transactions?"
  ]
}}}}

════════════════════════════════════════════════════════════
CONFIDENCE SCORING (Rule-Based)
════════════════════════════════════════════════════════════
High:   Sample size > 5% of total AND clear pattern (variance > 10%)
Medium: Sample size 1-5% OR moderate pattern (variance 5-10%)
Low:    Sample size < 1% OR weak pattern (variance < 5%)

Always explain your confidence level based on data quality.

════════════════════════════════════════════════════════════
REMEMBER
════════════════════════════════════════════════════════════
- Adapt your response structure to the question type
- Be concise but complete
- Use specific numbers, not vague terms
- Compare to benchmarks when relevant
- State limitations honestly
- Focus on actionable insights
- Return ONLY the JSON object, no extra text
"""


# ════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def strip_fences(raw: str) -> str:
    """
    Remove markdown code fences and extract only JSON content.
    Handles multiple formats:
    - ```json ... ```
    - ``` ... ```
    - Plain JSON with extra text after
    - Fixes common JSON errors (missing commas, extra spaces)
    """
    raw = raw.strip()
    
    # Remove markdown fences
    if raw.startswith("```"):
        raw = raw[3:]
        if raw.startswith("json"):
            raw = raw[4:]
        if raw.endswith("```"):
            raw = raw[:-3]
    
    raw = raw.strip()
    
    # Fix common JSON formatting issues
    # Fix: "strength" : "none" -> "strength": "none" (remove space before colon)
    import re
    raw = re.sub(r'"\s*:\s*', '": ', raw)
    
    # Extract only JSON content (handle extra text after JSON)
    # Find the last closing brace/bracket
    json_end = -1
    brace_count = 0
    bracket_count = 0
    in_string = False
    escape_next = False
    
    for i, char in enumerate(raw):
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    json_end = i + 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if brace_count == 0 and bracket_count == 0:
                    json_end = i + 1
    
    if json_end > 0:
        raw = raw[:json_end]
    
    return raw.strip()


def execute_pandas_query(df: pd.DataFrame, query_spec: dict) -> pd.DataFrame:
    """
    Execute Pandas operations based on query specification.
    
    Args:
        df: Source DataFrame
        query_spec: Dict from PANDAS_GENERATION_PROMPT
        
    Returns:
        Result DataFrame
    """
    result = df.copy()
    
    # Column name mapping (handle spaces in actual column names)
    column_map = {}
    for col in result.columns:
        # Create mapping: "transaction_type" -> "transaction type"
        normalized = col.lower().replace(' ', '_').replace('(', '').replace(')', '')
        column_map[normalized] = col
    
    # Apply filters
    if query_spec.get('filter_conditions'):
        for condition in query_spec['filter_conditions']:
            # Parse and apply filter
            condition = condition.strip()
            
            try:
                # Handle BETWEEN operator
                if '.between(' in condition.lower():
                    # Format: column.between(min, max)
                    col = condition.split('.between')[0].strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    # Extract min and max values
                    import re
                    match = re.search(r'between\(([^,]+),\s*([^)]+)\)', condition, re.IGNORECASE)
                    if match and actual_col in result.columns:
                        min_val = float(match.group(1).strip())
                        max_val = float(match.group(2).strip())
                        result = result[(result[actual_col] >= min_val) & (result[actual_col] <= max_val)]
                
                # Handle string contains
                elif '.str.contains(' in condition:
                    # Format: column.str.contains('value')
                    col = condition.split('.str.contains')[0].strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    import re
                    match = re.search(r"contains\(['\"]([^'\"]+)['\"]\)", condition)
                    if match and actual_col in result.columns:
                        search_val = match.group(1)
                        result = result[result[actual_col].str.contains(search_val, case=False, na=False)]
                
                # Handle string startswith
                elif '.str.startswith(' in condition:
                    col = condition.split('.str.startswith')[0].strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    import re
                    match = re.search(r"startswith\(['\"]([^'\"]+)['\"]\)", condition)
                    if match and actual_col in result.columns:
                        search_val = match.group(1)
                        result = result[result[actual_col].str.startswith(search_val, na=False)]
                
                # Handle string endswith
                elif '.str.endswith(' in condition:
                    col = condition.split('.str.endswith')[0].strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    import re
                    match = re.search(r"endswith\(['\"]([^'\"]+)['\"]\)", condition)
                    if match and actual_col in result.columns:
                        search_val = match.group(1)
                        result = result[result[actual_col].str.endswith(search_val, na=False)]
                
                # Handle date range filtering
                elif 'timestamp' in condition.lower() and '>=' in condition:
                    parts = condition.split('>=')
                    col = parts[0].strip()
                    date_val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    if actual_col in result.columns:
                        result[actual_col] = pd.to_datetime(result[actual_col], errors='coerce')
                        result = result[result[actual_col] >= pd.to_datetime(date_val)]
                
                elif 'timestamp' in condition.lower() and '<=' in condition:
                    parts = condition.split('<=')
                    col = parts[0].strip()
                    date_val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    if actual_col in result.columns:
                        result[actual_col] = pd.to_datetime(result[actual_col], errors='coerce')
                        result = result[result[actual_col] <= pd.to_datetime(date_val)]
                
                # Handle numeric comparisons
                elif '>=' in condition:
                    parts = condition.split('>=')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    try:
                        val = float(val)
                    except ValueError:
                        print(f"[WARNING] Cannot convert '{val}' to number for >= comparison")
                        continue
                    
                    if actual_col in result.columns:
                        result = result[result[actual_col] >= val]
                
                elif '<=' in condition:
                    parts = condition.split('<=')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    try:
                        val = float(val)
                    except ValueError:
                        continue
                    
                    if actual_col in result.columns:
                        result = result[result[actual_col] <= val]
                
                elif '>' in condition and '==' not in condition:
                    parts = condition.split('>')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    try:
                        val = float(val)
                    except ValueError:
                        continue
                    
                    if actual_col in result.columns:
                        result = result[result[actual_col] > val]
                
                elif '<' in condition and '==' not in condition:
                    parts = condition.split('<')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    try:
                        val = float(val)
                    except ValueError:
                        continue
                    
                    if actual_col in result.columns:
                        result = result[result[actual_col] < val]
                
                elif '==' in condition:
                    parts = condition.split('==')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    
                    if val.replace('.', '').replace('-', '').isdigit():
                        try:
                            val = float(val) if '.' in val else int(val)
                        except ValueError:
                            pass
                    
                    if actual_col in result.columns:
                        result = result[result[actual_col] == val]
                    
                elif '.notna()' in condition:
                    col = condition.replace('.notna()', '').strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    if actual_col in result.columns:
                        result = result[result[actual_col].notna()]
                    
                elif '.isin' in condition:
                    col = condition.split('.isin')[0].strip()
                    actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                    values_str = condition.split('.isin')[1].strip('() ')
                    # Simple parsing - extract values between quotes
                    import re
                    values = re.findall(r"'([^']*)'", values_str)
                    if actual_col in result.columns:
                        result = result[result[actual_col].isin(values)]
                
            except Exception as e:
                print(f"[ERROR] Failed to parse filter condition '{condition}': {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # For filter_segment operation (decomposition), return filtered data with breakdowns
    if query_spec.get('operation') == 'filter_segment':
        # Sort if specified
        if query_spec.get('sort_by'):
            sort_col = query_spec['sort_by']
            actual_sort_col = column_map.get(sort_col.lower().replace(' ', '_'), sort_col)
            if actual_sort_col in result.columns:
                result = result.sort_values(
                    actual_sort_col,
                    ascending=query_spec.get('sort_ascending', False)
                )
        
        # Apply limit
        limit = query_spec.get('limit')
        if limit is not None and len(result) > limit:
            result = result.head(limit)
        
        return result
    
    # Handle top_n_records operation (return individual records sorted)
    if query_spec.get('operation') == 'top_n_records':
        # Sort by specified column
        if query_spec.get('sort_by'):
            sort_col = query_spec['sort_by']
            actual_sort_col = column_map.get(sort_col.lower().replace(' ', '_'), sort_col)
            if actual_sort_col in result.columns:
                result = result.sort_values(
                    actual_sort_col,
                    ascending=query_spec.get('sort_ascending', False)
                )
        
        # Apply limit
        limit = query_spec.get('limit', 20)
        result = result.head(limit)
        
        # Select relevant columns for display
        display_cols = []
        for col in result.columns:
            col_lower = col.lower()
            # Include important columns
            if any(keyword in col_lower for keyword in ['id', 'amount', 'type', 'status', 'bank', 'timestamp', 'category']):
                display_cols.append(col)
        
        if display_cols:
            result = result[display_cols]
        
        return result
    
    # Handle aggregation operation (no groupby, just aggregate entire dataset)
    if query_spec.get('operation') == 'aggregation':
        metrics = query_spec.get('metrics', ['count'])
        
        # Find columns dynamically
        amount_col = None
        for col in result.columns:
            if 'amount' in col.lower():
                amount_col = col
                break
        
        id_col = None
        for col in result.columns:
            if 'transaction' in col.lower() and 'id' in col.lower():
                id_col = col
                break
        
        status_col = None
        for col in result.columns:
            if 'status' in col.lower():
                status_col = col
                break
        
        fraud_col = None
        for col in result.columns:
            if 'fraud' in col.lower():
                fraud_col = col
                break
        
        # Build aggregation result as a single-row DataFrame
        agg_result = {}
        if 'count' in metrics and id_col:
            agg_result['total_count'] = len(result)
        if 'failure_rate' in metrics and status_col:
            agg_result['failure_rate_pct'] = (result[status_col] == 'FAILED').mean() * 100
        if 'avg_amount' in metrics and amount_col:
            agg_result['avg_amount'] = result[amount_col].mean()
        if 'median_amount' in metrics and amount_col:
            agg_result['median_amount'] = result[amount_col].median()
        if 'std_amount' in metrics and amount_col:
            agg_result['std_amount'] = result[amount_col].std()
        if 'min_amount' in metrics and amount_col:
            agg_result['min_amount'] = result[amount_col].min()
        if 'max_amount' in metrics and amount_col:
            agg_result['max_amount'] = result[amount_col].max()
        if 'p25_amount' in metrics and amount_col:
            agg_result['p25_amount'] = result[amount_col].quantile(0.25)
        if 'p75_amount' in metrics and amount_col:
            agg_result['p75_amount'] = result[amount_col].quantile(0.75)
        if 'p95_amount' in metrics and amount_col:
            agg_result['p95_amount'] = result[amount_col].quantile(0.95)
        if 'fraud_rate' in metrics and fraud_col:
            agg_result['fraud_flag_rate_pct'] = result[fraud_col].mean() * 100
        
        # Return as single-row DataFrame
        return pd.DataFrame([agg_result])
    
    # Group by if specified
    if query_spec.get('group_by_column'):
        group_col = query_spec['group_by_column']
        
        # Handle both single column (string) and multiple columns (list)
        if isinstance(group_col, list):
            # Multiple columns - map each one
            actual_group_cols = []
            for col in group_col:
                actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                if actual_col in result.columns:
                    actual_group_cols.append(actual_col)
                else:
                    print(f"[WARNING] Group column '{col}' not found")
            
            if not actual_group_cols:
                print(f"[WARNING] No valid group columns found")
                return result
            
            actual_group_col = actual_group_cols
        else:
            # Single column
            actual_group_col = column_map.get(group_col.lower().replace(' ', '_'), group_col)
            
            if actual_group_col not in result.columns:
                print(f"[WARNING] Group column '{group_col}' not found")
                return result
        
        metrics = query_spec.get('metrics', ['count'])
        
        # Find amount column
        amount_col = None
        for col in result.columns:
            if 'amount' in col.lower():
                amount_col = col
                break
        
        # Find transaction_id column
        id_col = None
        for col in result.columns:
            if 'transaction' in col.lower() and 'id' in col.lower():
                id_col = col
                break
        
        # Find status column
        status_col = None
        for col in result.columns:
            if 'status' in col.lower():
                status_col = col
                break
        
        # Find fraud_flag column
        fraud_col = None
        for col in result.columns:
            if 'fraud' in col.lower():
                fraud_col = col
                break
        
        agg_dict = {}
        if 'count' in metrics and id_col:
            agg_dict['total_count'] = (id_col, 'count')
        if 'failure_rate' in metrics and status_col:
            agg_dict['failure_rate_pct'] = (
                status_col,
                lambda x: (x == 'FAILED').mean() * 100
            )
        if 'avg_amount' in metrics and amount_col:
            agg_dict['avg_amount'] = (amount_col, 'mean')
        if 'median_amount' in metrics and amount_col:
            agg_dict['median_amount'] = (amount_col, 'median')
        if 'std_amount' in metrics and amount_col:
            agg_dict['std_amount'] = (amount_col, 'std')
        if 'min_amount' in metrics and amount_col:
            agg_dict['min_amount'] = (amount_col, 'min')
        if 'max_amount' in metrics and amount_col:
            agg_dict['max_amount'] = (amount_col, 'max')
        if 'p25_amount' in metrics and amount_col:
            agg_dict['p25_amount'] = (amount_col, lambda x: x.quantile(0.25))
        if 'p75_amount' in metrics and amount_col:
            agg_dict['p75_amount'] = (amount_col, lambda x: x.quantile(0.75))
        if 'p95_amount' in metrics and amount_col:
            agg_dict['p95_amount'] = (amount_col, lambda x: x.quantile(0.95))
        if 'fraud_rate' in metrics and fraud_col:
            agg_dict['fraud_flag_rate_pct'] = (
                fraud_col,
                lambda x: x.mean() * 100
            )
        
        result = result.groupby(actual_group_col).agg(**agg_dict).reset_index()
        
        # Ensure result is valid
        if result is None or result.empty:
            print(f"[WARNING] Groupby returned empty result")
            return pd.DataFrame()
    
    # Ensure result is a DataFrame at this point
    if not isinstance(result, pd.DataFrame):
        print(f"[WARNING] Result is not a DataFrame: {type(result)}")
        return pd.DataFrame()
    
    # Sort
    if query_spec.get('sort_by'):
        sort_col = query_spec['sort_by']
        actual_sort_col = column_map.get(sort_col.lower().replace(' ', '_'), sort_col)
        if actual_sort_col in result.columns:
            result = result.sort_values(
                actual_sort_col,
                ascending=query_spec.get('sort_ascending', False)
            )
    
    # Limit (only if result is valid and limit is specified)
    limit = query_spec.get('limit')
    if limit is not None and not result.empty:
        if query_spec.get('operation') != 'filter_segment' and len(result) > limit:
            result = result.head(limit)
    
    # Return valid DataFrame
    if result.empty:
        return pd.DataFrame()
    
    return result
