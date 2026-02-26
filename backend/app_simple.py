from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import json

# Try to import Multi-LLM service
try:
    from multi_llm_service import MultiLLMService
    llm_available = True
except ImportError as e:
    print(f"[WARNING] Multi-LLM service not available: {e}")
    llm_available = False

# Import advanced prompts system
try:
    from advanced_prompts import (
        get_global_stats,
        build_insight_prompt,
        PANDAS_GENERATION_PROMPT,
        strip_fences,
        execute_pandas_query
    )
    advanced_prompts_available = True
except ImportError as e:
    print(f"[WARNING] Advanced prompts not available: {e}")
    advanced_prompts_available = False

app = Flask(__name__)
CORS(app)

# Initialize Multi-LLM Service if available
llm_service = None
if llm_available:
    try:
        OPENROUTER_API_KEY = "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"
        GEMINI_API_KEY = "AIzaSyCl4ptHWz4T1jK3oSexnCyJ73UUOJQofU4"
        llm_service = MultiLLMService(
            openrouter_key=OPENROUTER_API_KEY,
            gemini_key=GEMINI_API_KEY
        )
    except Exception as e:
        print(f"[WARNING] Could not initialize Multi-LLM service: {e}")
        llm_service = None

# Global stats cache
global_stats = None

# Conversation history (in-memory, per session)
# In production, use Redis or database
conversation_history = []

# Auto-load dataset on startup
print("=" * 50)
print("Loading transactions.csv...")

# Try multiple possible paths
possible_paths = [
    'data/upi_transactions_2024.csv',
    'backend/data/upi_transactions_2024.csv',
    '../data/upi_transactions_2024.csv',
    'data/transactions.csv',
    'backend/data/transactions.csv'
]

df = None
dataset_loaded = False

for path in possible_paths:
    try:
        df = pd.read_csv(path)
        dataset_loaded = True
        print(f"[OK] Dataset loaded from: {path}")
        print(f"[OK] Rows: {len(df):,}")
        print(f"[OK] Columns: {len(df.columns)}")
        print(f"[OK] Column names: {', '.join(df.columns.tolist())}")
        
        # Compute global stats for advanced prompts
        if advanced_prompts_available:
            global_stats = get_global_stats(df)
            print(f"[OK] Global stats computed:")
            print(f"    - Total transactions: {global_stats['total_transactions']:,}")
            print(f"    - Overall failure rate: {global_stats['overall_failure_rate_pct']}%")
            print(f"    - Overall fraud rate: {global_stats['overall_fraud_flag_rate_pct']}%")
        
        break
    except FileNotFoundError:
        continue
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {str(e)}")

if not dataset_loaded:
    print("[ERROR] transactions.csv not found!")
    print("[ERROR] Please place CSV file in backend/data/ folder")
    print("=" * 50)
else:
    print("=" * 50)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "ok", 
        "message": "Backend is running",
        "dataset_loaded": dataset_loaded,
        "rows": len(df) if dataset_loaded else 0
    })

@app.route('/columns', methods=['GET'])
def get_columns():
    """Get column names - dataset is always loaded"""
    if not dataset_loaded:
        return jsonify({"error": "Dataset not loaded"}), 500
    
    columns = []
    for col in df.columns:
        columns.append({
            'name': col,
            'type': str(df[col].dtype)
        })
    
    return jsonify({
        "columns": columns,
        "rows": len(df)
    })

@app.route('/models', methods=['GET'])
def get_models():
    """Get available AI models"""
    if llm_service:
        return jsonify(llm_service.get_available_models())
    return jsonify({"models": []})

@app.route('/query', methods=['POST'])
def process_query():
    global df, dataset_loaded
    
    if not dataset_loaded:
        return jsonify({
            "answer": "Dataset not loaded. Please check backend/data/ folder.",
            "statistics": None
        })
    
    try:
        data = request.json
        query = data.get('query', '').lower()
        use_ai = data.get('use_ai', True)
        model = data.get('model', 'deepseek-r1')  # Default to DeepSeek R1
        
        # If AI is enabled and available, use Multi-LLM service
        if use_ai and llm_service:
            try:
                # Get the actual amount column name
                amount_col = None
                for col in df.columns:
                    if 'amount' in col.lower():
                        amount_col = col
                        break
                
                # Prepare data context for LLM
                total_amount = df[amount_col].sum() if amount_col else 0
                avg_amount = df[amount_col].mean() if amount_col else 0
                
                data_context = f"""
Dataset: UPI Transaction Data
Total Transactions: {len(df):,}
Columns: {', '.join(df.columns.tolist())}
Total Amount: Rs.{total_amount:,.2f}
Average Amount: Rs.{avg_amount:.2f}

Sample Data (first 3 rows):
{df.head(3).to_string()}

Key Statistics:
- Fraud transactions: {df['fraud_flag'].sum() if 'fraud_flag' in df.columns else 'N/A'}
- Unique merchants: {df['merchant_category'].nunique() if 'merchant_category' in df.columns else 'N/A'}
- Date range: {df['timestamp'].min() if 'timestamp' in df.columns else 'N/A'} to {df['timestamp'].max() if 'timestamp' in df.columns else 'N/A'}
"""
                
                # Query with selected model
                result = llm_service.query(query, data_context, model=model)
                return jsonify(result)
            except Exception as e:
                print(f"[WARNING] LLM query failed: {e}")
                # Fall through to simple processing
        
        # Fallback to simple query processing
        response = {"answer": "", "statistics": {}}
        
        # Find amount column dynamically
        amount_col = None
        for col in df.columns:
            if 'amount' in col.lower():
                amount_col = col
                break
        
        if 'average' in query or 'mean' in query:
            if 'amount' in query and amount_col:
                avg = df[amount_col].mean()
                response['answer'] = f"The average transaction amount is Rs.{avg:.2f}"
                response['statistics'] = {
                    'Average Amount': f"Rs.{avg:.2f}",
                    'Total Transactions': len(df)
                }
        
        elif 'total' in query or 'sum' in query:
            if 'amount' in query and amount_col:
                total = df[amount_col].sum()
                response['answer'] = f"The total transaction amount is Rs.{total:,.2f}"
                response['statistics'] = {
                    'Total Amount': f"Rs.{total:,.2f}",
                    'Transaction Count': len(df)
                }
        
        elif 'count' in query or 'how many' in query:
            count = len(df)
            response['answer'] = f"There are {count:,} transactions in the dataset"
            response['statistics'] = {
                'Total Transactions': count
            }
        
        else:
            # Default response
            response['answer'] = f"Dataset contains {len(df):,} transactions with {len(df.columns)} columns"
            response['statistics'] = {
                'Total Transactions': len(df),
                'Columns': len(df.columns)
            }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            "answer": f"Error: {str(e)}",
            "statistics": None
        })

@app.route('/query-status/<job_id>', methods=['GET'])
def get_query_status(job_id):
    """Get status of background reasoning job"""
    if llm_service:
        status = llm_service.get_job_status(job_id)
        return jsonify(status)
    return jsonify({"status": "not_available", "message": "LLM service not initialized"})

@app.route('/advanced-query', methods=['POST'])
def advanced_query():
    """
    Advanced query endpoint using production-grade prompts.
    Returns 10/10 quality insights with:
    - Volume validation
    - Domain reasoning
    - Specific recommendations
    - Confidence scoring
    - Follow-up questions
    """
    global df, dataset_loaded, global_stats, conversation_history
    
    if not dataset_loaded:
        return jsonify({
            "status": "error",
            "error": "Dataset not loaded"
        })
    
    if not advanced_prompts_available or not llm_service:
        return jsonify({
            "status": "error",
            "error": "Advanced prompts or LLM service not available"
        })
    
    try:
        data = request.json
        user_question = data.get('query', '')
        model = data.get('model', 'auto')  # auto, deepseek-r1, deepseek-chat, gemini-flash
        
        print(f"\n[ADVANCED QUERY] Question: {user_question}")
        print(f"[ADVANCED QUERY] Model: {model}")
        
        # STEP 1: Generate Pandas query specification
        print("[STEP 1] Generating query specification...")
        
        query_resp = llm_service.openrouter_client.chat.completions.create(
            model="deepseek/deepseek-chat",
            max_tokens=1200,
            temperature=0.1,
            messages=[
                {"role": "system", "content": PANDAS_GENERATION_PROMPT},
                {"role": "user", "content": user_question}
            ]
        )
        
        raw_query = query_resp.choices[0].message.content
        raw_query = strip_fences(raw_query)
        
        print(f"[DEBUG] Raw query response (first 200 chars): {raw_query[:200]}")
        
        try:
            query_spec = json.loads(raw_query)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse query spec: {e}")
            print(f"[ERROR] Raw content: {raw_query}")
            return jsonify({
                "status": "error",
                "error": f"Failed to parse query specification: {str(e)}",
                "raw_response": raw_query[:500]
            })
        
        if query_spec.get("status") == "error":
            return jsonify({
                "status": "error",
                "error": query_spec.get("reason", "Query cannot be answered"),
                "suggestion": query_spec.get("suggestion", "Try rephrasing")
            })
        
        print(f"[STEP 1] Query spec: {query_spec['operation']}")
        
        # STEP 2: Execute Pandas query
        print("[STEP 2] Executing Pandas query...")
        result_df = execute_pandas_query(df, query_spec)
        
        if result_df.empty:
            return jsonify({
                "status": "empty",
                "message": "No data found for this query. Try broadening your filters."
            })
        
        print(f"[STEP 2] Result: {len(result_df)} rows")
        
        # STEP 3: Generate advanced insight
        print("[STEP 3] Generating advanced insight...")
        
        # Select model based on auto-classification or user choice
        if model == 'auto':
            insight_model, reason = llm_service.classify_query(user_question)
            print(f"[AUTO] Selected {insight_model}: {reason}")
        else:
            insight_model = model
        
        # Use DeepSeek R1 for complex insights
        if insight_model == 'deepseek-r1':
            model_name = "deepseek/deepseek-r1"
        elif insight_model == 'gemini-flash':
            model_name = "gemini-2.5-flash"
        else:
            model_name = "deepseek/deepseek-chat"
        
        # Build insight prompt with global stats
        insight_system_prompt = build_insight_prompt(global_stats)
        
        # Prepare data summary for LLM
        data_summary = f"""Query Result ({len(result_df)} rows):
{result_df.to_string(index=False)}

Numeric Totals:
{result_df.select_dtypes(include=['number']).sum().to_string()}

Column Types:
{result_df.dtypes.to_string()}
"""
        
        insight_resp = llm_service.openrouter_client.chat.completions.create(
            model=model_name,
            max_tokens=3000,
            temperature=0.3,
            messages=[
                {"role": "system", "content": insight_system_prompt},
                {"role": "user", "content": f"""Original Question: {user_question}

{data_summary}

IMPORTANT: Respond ONLY in English. Do not use Chinese, Hindi, or any other language.
All field values, recommendations, and explanations must be in English.

Now analyze this result following the 7-step reasoning chain.
Generate the structured insight JSON with:
- Volume validation (segment % of total)
- Domain reasoning (WHY patterns exist)
- Specific recommendations (HOW to fix)
- Confidence scoring (rule-based)
- Follow-up questions

Remember: use ONLY numbers from this result and the global benchmarks.
State data limitations honestly. Never fabricate impact percentages.
All text must be in English."""}
            ]
        )
        
        # Extract reasoning chain if available (DeepSeek R1)
        reasoning_chain = ""
        msg = insight_resp.choices[0].message
        if hasattr(msg, "reasoning_content") and msg.reasoning_content:
            reasoning_chain = msg.reasoning_content
        
        raw_insight = msg.content
        raw_insight = strip_fences(raw_insight)
        
        print(f"[DEBUG] Raw insight response (first 200 chars): {raw_insight[:200]}")
        
        try:
            insight = json.loads(raw_insight)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse insight: {e}")
            print(f"[ERROR] Raw content: {raw_insight}")
            return jsonify({
                "status": "error",
                "error": f"Failed to parse insight JSON: {str(e)}",
                "raw_response": raw_insight[:500],
                "reasoning_chain": reasoning_chain
            })
        
        print("[STEP 3] Insight generated successfully")
        
        # STEP 4: Update conversation history
        conversation_history.append({
            "role": "user",
            "content": user_question
        })
        conversation_history.append({
            "role": "assistant",
            "content": insight.get("direct_answer", "")
        })
        
        # Keep last 12 messages (6 turns)
        if len(conversation_history) > 12:
            conversation_history = conversation_history[-12:]
        
        return jsonify({
            "status": "success",
            "insight": insight,
            "reasoning_chain": reasoning_chain,
            "data": result_df.to_dict('records'),
            "chart_type": query_spec.get("chart_type", "vertical_bar"),
            "intent": query_spec.get("intent", "analysis"),
            "model_used": insight_model,
            "rows_returned": len(result_df)
        })
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse error: {e}")
        return jsonify({
            "status": "error",
            "error": f"Failed to parse response: {str(e)}"
        })
    except Exception as e:
        print(f"[ERROR] Advanced query failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": str(e)
        })

@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear LLM query cache"""
    if llm_service:
        result = llm_service.clear_cache()
        return jsonify(result)
    return jsonify({"message": "LLM service not available"})

if __name__ == '__main__':
    print("=" * 50)
    print("InsightX Backend Server")
    print("Running on http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000, use_reloader=False)
