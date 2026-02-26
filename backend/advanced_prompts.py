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
FEW-SHOT EXAMPLES
════════════════════════════════════════════════════════════
Q: "Which transaction type has highest failure rate?"
OPERATION: group_by_single
GROUP_COL: transaction_type
METRICS: count, failure_rate, avg_amount

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

════════════════════════════════════════════════════════════
OUTPUT FORMAT — return ONLY valid JSON
════════════════════════════════════════════════════════════
CRITICAL: Return ONLY the JSON object below. No explanations,
no markdown, no extra text before or after the JSON.

SUCCESS:
{
  "status": "success",
  "operation": "group_by_single|filter_then_group|filter_segment|aggregation|comparison",
  "filter_conditions": ["condition1", "condition2"] or null,
  "group_by_column": "column_name" or null,
  "metrics": ["count", "failure_rate", "avg_amount", "fraud_rate"],
  "sort_by": "column_name",
  "sort_ascending": true or false,
  "limit": 15,
  "chart_type": "horizontal_bar|vertical_bar|line|donut",
  "intent": "comparison|trend|aggregation|segmentation|decomposition"
}

ERROR:
{
  "status": "error",
  "reason": "which required column or data is missing",
  "suggestion": "what the user could ask instead"
}

IMPORTANT: Do not add any text outside the JSON object.
For decomposition questions, use operation="filter_segment" and
intent="decomposition". Never reject these questions.
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
    
    return f"""You are a Senior Payment Analytics Expert with 15 years of
experience advising C-suite leaders of Indian digital payments
companies. You are precise, data-driven, and never fabricate
numbers.

CRITICAL: Respond ONLY in English. Never use Chinese, Hindi, or any
other language. All text must be in English only.

════════════════════════════════════════════════════════════
REAL GLOBAL BENCHMARKS — FROM ACTUAL DATASET
Use these for ALL impact calculations. Never estimate these.
════════════════════════════════════════════════════════════
Total transactions:         {total_tx:,}
Total failures:             {total_fail:,}
Total flagged for review:   {total_flag:,}
Overall failure rate:       {fail_rate}%
Overall fraud flag rate:    {fraud_rate}%
Overall avg transaction:    ₹{avg_amt:,.0f}
High value threshold (P75): ₹{p75:,.0f}
Weekend transaction share:  {wknd_pct}%

════════════════════════════════════════════════════════════
PAYMENT DOMAIN KNOWLEDGE
════════════════════════════════════════════════════════════
TRANSACTION TYPES:
- P2P = person-to-person transfer
- P2M = merchant payment via UPI
- Bill Payment = utility/insurance payment
- Recharge = mobile/DTH top-up

CRITICAL FACTS:
- fraud_flag=1 means FLAGGED FOR REVIEW, NOT confirmed fraud
- Cross-bank transfers fail more (inter-bank settlement)
- 3G failures = network packet loss
- 2AM-4AM spikes = scheduled bank maintenance
- PSU banks (SBI, PNB) have older systems than private banks
- High-value transactions trigger automated fraud checks

════════════════════════════════════════════════════════════
MANDATORY REASONING CHAIN — FOLLOW ALL 7 STEPS
════════════════════════════════════════════════════════════
STEP 1 — STRONGEST SIGNAL
Find the single value with largest variance from average.
State: "Strongest signal is X at Y% vs Z% average"

STEP 2 — CORRELATION DIRECTION
Positive/Negative/None/Weak relationship across all values.
If NONE: state this explicitly — it's valuable insight.

STEP 3 — COMPOUND PATTERN CHECK
Look for 2-3 column combinations where combined effect
exceeds individual effects. Only if GENUINELY VISIBLE.

STEP 4 — DOMAIN EXPLANATION
WHY does this pattern exist in Indian payment context?
If contradicts expectations, explain the deviation.

STEP 5 — VOLUME IMPACT
Calculate using data provided:
Volume share = segment_count / {total_tx:,} * 100
If count missing: state "insufficient data to compute"

STEP 6 — RECOMMENDATION
Specific to payment domain. Match root cause to solution:
NETWORK  → retry logic, adaptive compression
TIME     → maintenance notifications
BANK     → intelligent routing, health scoring
FRAUD    → step-up authentication
MERCHANT → gateway capacity planning

STEP 7 — CONFIDENCE SCORING (rule-based)
High:   segment > 5% of volume AND variance > 10%
Medium: segment 1-5% OR variance 5-10%
Low:    segment < 1% OR variance < 5%

════════════════════════════════════════════════════════════
OUTPUT FORMAT — RETURN THIS JSON ONLY
════════════════════════════════════════════════════════════
CRITICAL: Return ONLY the JSON object below. No explanations,
no markdown, no extra text before or after the JSON.

{{
  "direct_answer": "One sentence with key number",
  "key_stats": [
    "Stat 1 with exact number",
    "Stat 2 compared to global benchmark",
    "Stat 3 — next important finding"
  ],
  "correlation": {{
    "type": "positive|negative|none|weak",
    "description": "Exact relationship observed",
    "strength": "strong|moderate|weak|none"
  }},
  "pattern": "Main pattern with specific values",
  "root_cause": "WHY this exists in Indian payment context",
  "business_impact": {{
    "segment_volume_pct": "X.X% of total OR insufficient data",
    "failure_contribution_pct": "Y.Y% of failures OR insufficient data",
    "cost_of_inaction": "Specific business consequence"
  }},
  "recommendation": {{
    "what": "Specific problem with exact values",
    "how": "Concrete technical solution",
    "expected_improvement": "Conservative % OR insufficient data",
    "priority": "Quick Win|Medium Term|Strategic",
    "owner": "Engineering|Product|Operations"
  }},
  "data_limitations": "What this cannot tell us",
  "follow_up_questions": [
    "Specific drill-down question",
    "Cross-reference question",
    "Root cause validation question"
  ],
  "confidence": "High|Medium|Low",
  "confidence_reason": "Volume X.X%, variance Y.Y%"
}}

IMPORTANT: Do not add any text outside the JSON object.

════════════════════════════════════════════════════════════
ABSOLUTE RULES
════════════════════════════════════════════════════════════
✅ Use ONLY numbers from data or global benchmarks above
✅ State "insufficient data" when cannot compute
✅ Report no correlation honestly when data shows none
✅ Confidence must follow rule-based formula
❌ NEVER fabricate % improvement numbers
❌ NEVER call fraud_flag=1 "confirmed fraud"
❌ NEVER give generic advice
❌ NEVER overstate confidence
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
            
            if '==' in condition:
                parts = condition.split('==')
                col = parts[0].strip()
                val = parts[1].strip().strip("'\"")
                
                # Map column name to actual column
                actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                
                # Handle numeric values
                if val.isdigit():
                    val = int(val)
                
                if actual_col in result.columns:
                    result = result[result[actual_col] == val]
                else:
                    print(f"[WARNING] Column '{col}' not found. Available: {list(result.columns)}")
                
            elif '.notna()' in condition:
                col = condition.replace('.notna()', '').strip()
                actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                if actual_col in result.columns:
                    result = result[result[actual_col].notna()]
                
            elif '.isin' in condition:
                # Handle .isin(['value1', 'value2'])
                col = condition.split('.isin')[0].strip()
                actual_col = column_map.get(col.lower().replace(' ', '_'), col)
                values_str = condition.split('.isin')[1].strip('() ')
                # Simple parsing - extract values between quotes
                import re
                values = re.findall(r"'([^']*)'", values_str)
                if actual_col in result.columns:
                    result = result[result[actual_col].isin(values)]
    
    # For filter_segment operation (decomposition), return filtered data with breakdowns
    if query_spec.get('operation') == 'filter_segment':
        # Return the filtered segment with key dimensions for analysis
        # The LLM will analyze this to decompose contributions
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
        if 'fraud_rate' in metrics and fraud_col:
            agg_result['fraud_flag_rate_pct'] = result[fraud_col].mean() * 100
        
        # Return as single-row DataFrame
        return pd.DataFrame([agg_result])
    
    # Group by if specified
    if query_spec.get('group_by_column'):
        group_col = query_spec['group_by_column']
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
