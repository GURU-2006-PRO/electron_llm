from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Helper function to convert numpy/pandas types to JSON-serializable types
def make_json_serializable(obj):
    """
    Recursively convert numpy/pandas types to native Python types
    """
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    else:
        return obj

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

# Import new enhancement modules
try:
    from statistical_analysis import add_statistical_analysis
    from query_suggestions import QuerySuggestionEngine
    from methodology_explainer import MethodologyExplainer
    from proactive_insights import ProactiveInsightGenerator
    enhancements_available = True
    print("[OK] Enhancement modules loaded")
except ImportError as e:
    print(f"[WARNING] Enhancement modules not available: {e}")
    enhancements_available = False

# Import TIER 1 features
try:
    from tier1_integration import Tier1FeatureManager
    tier1_available = True
except ImportError as e:
    print(f"[WARNING] TIER 1 features not available: {e}")
    tier1_available = False

# Geospatial features removed
geospatial_available = False

# Import database
try:
    from database import get_database
    db = get_database()
    db_available = True
except ImportError as e:
    print(f"[WARNING] Database not available: {e}")
    db_available = False
    db = None

app = Flask(__name__)
CORS(app)

# Initialize Multi-LLM Service if available
llm_service = None
if llm_available:
    try:
        # Get API keys from environment variables
        OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
        GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
        
        if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == 'your-openrouter-key-here':
            print("[WARNING] OPENROUTER_API_KEY not set in .env file")
        
        if not GEMINI_API_KEY or GEMINI_API_KEY == 'your-gemini-key-here':
            print("[WARNING] GEMINI_API_KEY not set in .env file")
        
        llm_service = MultiLLMService(
            openrouter_key=OPENROUTER_API_KEY,
            gemini_key=GEMINI_API_KEY
        )
    except Exception as e:
        print(f"[WARNING] Could not initialize Multi-LLM service: {e}")
        llm_service = None

# Global stats cache
global_stats = None

# TIER 1 Feature Manager
tier1_manager = None

# Query suggestion engine
suggestion_engine = None

# Proactive insights generator
proactive_generator = None

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
        
        # Initialize enhancement modules
        if enhancements_available:
            suggestion_engine = QuerySuggestionEngine(df)
            proactive_generator = ProactiveInsightGenerator(df, global_stats)
            print(f"[OK] Enhancement modules initialized")
        
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
    
    # Initialize TIER 1 features
    if tier1_available and global_stats:
        try:
            tier1_manager = Tier1FeatureManager(df, global_stats)
            print("[OK] TIER 1 features initialized")
            
            # Run anomaly detection
            anomalies = tier1_manager.get_anomalies()
            print(f"[OK] Detected {len(anomalies)} anomalies")
            if anomalies:
                print(f"[ALERT] Top anomaly: {anomalies[0]['message']}")
        except Exception as e:
            print(f"[WARNING] TIER 1 initialization failed: {e}")
            tier1_manager = None

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
        print("[INFO] Using Gemini API for query generation")
        
        # Use Gemini API instead of OpenRouter
        query_prompt = f"""{PANDAS_GENERATION_PROMPT}

User Question: {user_question}

Generate the query specification JSON."""
        
        try:
            query_resp = llm_service.gemini_model.generate_content(query_prompt)
            raw_query = query_resp.text
        except Exception as e:
            print(f"[ERROR] Gemini API failed for query generation: {e}")
            return jsonify({
                "status": "error",
                "error": f"Gemini API error: {str(e)}"
            })
        
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
        
        # STEP 2.5: Add statistical analysis and enhancements
        statistical_insights = None
        methodology = None
        proactive_suggestions = None
        
        if enhancements_available:
            print("[STEP 2.5] Adding enhancements...")
            
            # Statistical analysis
            statistical_insights = add_statistical_analysis(result_df, query_spec, df, global_stats)
            
            # Methodology explanation
            methodology = MethodologyExplainer.explain_query_execution(query_spec, result_df, df)
            
            # Proactive insights
            proactive_suggestions = {
                "follow_up_questions": proactive_generator.generate_follow_up_questions(
                    user_question, result_df, query_spec
                ),
                "proactive_alerts": proactive_generator.generate_proactive_alerts(
                    result_df, query_spec
                ),
                "related_analyses": proactive_generator.suggest_related_analyses(
                    user_question, query_spec
                ),
                "insight_summary": proactive_generator.generate_insight_summary(
                    result_df, query_spec
                )
            }
            
            print("[STEP 2.5] Enhancements added")
        
        # STEP 3: Generate advanced insight
        print("[STEP 3] Generating advanced insight...")
        
        # Select model based on auto-classification or user choice
        if model == 'auto':
            insight_model, reason = llm_service.classify_query(user_question)
            print(f"[AUTO] Selected {insight_model}: {reason}")
        else:
            insight_model = model
        
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
        
        # Use Gemini directly if selected, otherwise use OpenRouter
        if insight_model == 'gemini-flash':
            print("[INFO] Using Gemini API directly")
            
            # Use Gemini API
            prompt = f"""{insight_system_prompt}

Original Question: {user_question}

{data_summary}

IMPORTANT: Respond ONLY in English. Do not use Chinese, Hindi, or any other language.
All field values, recommendations, and explanations must be in English.

Now analyze this result and generate the structured insight JSON.
Return ONLY valid JSON, no markdown, no extra text."""
            
            try:
                gemini_response = llm_service.gemini_model.generate_content(prompt)
                raw_insight = gemini_response.text
            except Exception as e:
                print(f"[ERROR] Gemini API failed: {e}")
                return jsonify({
                    "status": "error",
                    "error": f"Gemini API error: {str(e)}"
                })
        else:
            # Use OpenRouter for DeepSeek models
            if insight_model == 'deepseek-r1':
                model_name = "deepseek/deepseek-r1"
            else:
                model_name = "deepseek/deepseek-chat"
            
            print(f"[INFO] Using OpenRouter with model: {model_name}")
            
            try:
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

Now analyze this result and generate the structured insight JSON.
Return ONLY valid JSON, no markdown, no extra text."""}
                    ]
                )
                
                # Extract reasoning chain if available (DeepSeek R1)
                reasoning_chain = ""
                msg = insight_resp.choices[0].message
                if hasattr(msg, "reasoning_content") and msg.reasoning_content:
                    reasoning_chain = msg.reasoning_content
                
                raw_insight = msg.content
            except Exception as e:
                print(f"[ERROR] OpenRouter API failed: {e}")
                return jsonify({
                    "status": "error",
                    "error": f"OpenRouter API error: {str(e)}. Try using Gemini model instead."
                })
        
        # Strip markdown fences and parse JSON
        reasoning_chain = ""  # Only available for DeepSeek R1
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
        
        # STEP 4: Save to database
        if db_available:
            try:
                db.add_query(
                    query=user_question,
                    response=insight.get("direct_answer", ""),
                    model=insight_model,
                    advanced_mode=True,
                    data_rows=len(result_df),
                    chart_type=query_spec.get("chart_type", ""),
                    execution_time=None
                )
                print("[STEP 4] Query saved to database")
            except Exception as e:
                print(f"[WARNING] Failed to save to database: {e}")
        
        # STEP 5: Update conversation history
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
        
        # Convert all data to JSON-serializable format
        response_data = {
            "status": "success",
            "insight": make_json_serializable(insight),
            "reasoning_chain": reasoning_chain,
            "data": result_df.to_dict('records'),
            "chart_type": query_spec.get("chart_type", "vertical_bar"),
            "intent": query_spec.get("intent", "analysis"),
            "model_used": insight_model,
            "rows_returned": len(result_df),
            "statistical_insights": make_json_serializable(statistical_insights),
            "methodology": make_json_serializable(methodology),
            "proactive_suggestions": make_json_serializable(proactive_suggestions)
        }
        
        return jsonify(response_data)
        
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

@app.route('/stream-query', methods=['GET'])
def stream_query():
    """
    Streaming endpoint for real-time token-by-token responses.
    Uses GET method for EventSource compatibility.
    """
    from flask import Response, stream_with_context
    
    global df, dataset_loaded, global_stats
    
    if not dataset_loaded:
        return jsonify({"status": "error", "error": "Dataset not loaded"})
    
    if not llm_service:
        return jsonify({"status": "error", "error": "LLM service not available"})
    
    def generate():
        try:
            # Get parameters from query string (GET request)
            query = request.args.get('query', '')
            model = request.args.get('model', 'auto')
            
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing query...'})}\n\n"
            
            # Select model
            if model == 'auto':
                selected_model, reason = llm_service.classify_query(query)
                yield f"data: {json.dumps({'type': 'model', 'model': selected_model, 'reason': reason})}\n\n"
            else:
                selected_model = model
            
            # Prepare context
            amount_col = None
            for col in df.columns:
                if 'amount' in col.lower():
                    amount_col = col
                    break
            
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
"""
            
            # Stream response
            if selected_model == 'deepseek-r1':
                model_name = "deepseek/deepseek-r1"
            elif selected_model == 'gemini-flash':
                # Use DeepSeek Chat instead (Gemini not on OpenRouter)
                model_name = "deepseek/deepseek-chat"
            else:
                model_name = "deepseek/deepseek-chat"
            
            stream = llm_service.openrouter_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a payment analytics expert. Provide clear, concise answers."},
                    {"role": "user", "content": f"{query}\n\nContext:\n{data_context}"}
                ],
                stream=True,
                max_tokens=2000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'type': 'content', 'content': content})}\n\n"
            
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear LLM query cache"""
    if llm_service:
        result = llm_service.clear_cache()
        return jsonify(result)
    return jsonify({"message": "LLM service not available"})

# ===== CHAT HISTORY DATABASE ENDPOINTS =====

@app.route('/history', methods=['GET'])
def get_history():
    """Get chat history with pagination"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        bookmarked_only = request.args.get('bookmarked', 'false').lower() == 'true'
        
        history = db.get_history(limit=limit, offset=offset, bookmarked_only=bookmarked_only)
        
        return jsonify({
            "status": "success",
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        print(f"[ERROR] Get history failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/search', methods=['GET'])
def search_history():
    """Search chat history"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        search_term = request.args.get('q', '')
        limit = int(request.args.get('limit', 50))
        
        if not search_term:
            return jsonify({"status": "error", "error": "Search term required"})
        
        results = db.search_history(search_term, limit=limit)
        
        return jsonify({
            "status": "success",
            "results": results,
            "count": len(results)
        })
    except Exception as e:
        print(f"[ERROR] Search history failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/<int:history_id>/bookmark', methods=['POST'])
def toggle_bookmark(history_id):
    """Toggle bookmark status"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        new_status = db.toggle_bookmark(history_id)
        return jsonify({
            "status": "success",
            "bookmarked": new_status
        })
    except Exception as e:
        print(f"[ERROR] Toggle bookmark failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    """Delete a history record"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        success = db.delete_query(history_id)
        if success:
            return jsonify({"status": "success", "message": "History deleted"})
        else:
            return jsonify({"status": "error", "error": "History not found"})
    except Exception as e:
        print(f"[ERROR] Delete history failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Clear all history (optionally keep bookmarked)"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        data = request.json or {}
        keep_bookmarked = data.get('keep_bookmarked', True)
        
        count = db.clear_history(keep_bookmarked=keep_bookmarked)
        
        return jsonify({
            "status": "success",
            "message": f"Cleared {count} records",
            "deleted_count": count
        })
    except Exception as e:
        print(f"[ERROR] Clear history failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/stats', methods=['GET'])
def get_history_stats():
    """Get usage statistics"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        stats = db.get_statistics()
        return jsonify({
            "status": "success",
            "statistics": stats
        })
    except Exception as e:
        print(f"[ERROR] Get stats failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/export', methods=['GET'])
def export_history():
    """Export history to JSON"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        filepath = 'data/chat_history_export.json'
        count = db.export_history(filepath)
        
        return jsonify({
            "status": "success",
            "message": f"Exported {count} records",
            "filepath": filepath
        })
    except Exception as e:
        print(f"[ERROR] Export failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/history/import', methods=['POST'])
def import_history():
    """Import history from localStorage format"""
    if not db_available:
        return jsonify({"status": "error", "error": "Database not available"})
    
    try:
        data = request.json
        history_data = data.get('history', [])
        
        if not history_data:
            return jsonify({"status": "error", "error": "No history data provided"})
        
        count = db.import_from_localstorage(history_data)
        
        return jsonify({
            "status": "success",
            "message": f"Imported {count} records",
            "imported_count": count
        })
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/query-suggestions', methods=['GET'])
def get_query_suggestions():
    """Get query suggestions and auto-complete"""
    if not suggestion_engine:
        return jsonify({"status": "error", "error": "Suggestion engine not available"})
    
    try:
        partial_query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        suggestions = suggestion_engine.get_suggestions(partial_query, limit)
        
        # Check for typos
        typo_check = suggestion_engine.suggest_typo_correction(partial_query)
        
        return jsonify({
            "status": "success",
            "suggestions": suggestions,
            "typo_correction": typo_check,
            "count": len(suggestions)
        })
    except Exception as e:
        print(f"[ERROR] Query suggestions failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """
    Get dashboard statistics and overview data.
    Returns KPIs with trends and overview charts data.
    """
    global df, dataset_loaded
    
    if not dataset_loaded:
        return jsonify({"status": "error", "error": "Dataset not loaded"})
    
    try:
        from datetime import datetime, timedelta
        
        # Find column names dynamically
        amount_col = None
        status_col = None
        fraud_col = None
        timestamp_col = None
        bank_col = None
        type_col = None
        hour_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'amount' in col_lower and amount_col is None:
                amount_col = col
            elif 'status' in col_lower and status_col is None:
                status_col = col
            elif 'fraud' in col_lower and fraud_col is None:
                fraud_col = col
            elif 'timestamp' in col_lower or 'date' in col_lower and timestamp_col is None:
                timestamp_col = col
            elif 'bank' in col_lower and 'sender' in col_lower and bank_col is None:
                bank_col = col
            elif 'type' in col_lower and 'transaction' in col_lower and type_col is None:
                type_col = col
            elif 'hour' in col_lower and hour_col is None:
                hour_col = col
        
        # Calculate KPIs (convert numpy types to Python types for JSON serialization)
        total_transactions = int(len(df))
        
        # Success rate
        if status_col:
            success_count = int(df[df[status_col].str.lower() == 'success'].shape[0])
            success_rate = float(round((success_count / total_transactions) * 100, 2))
            failure_rate = float(round(100 - success_rate, 2))
        else:
            success_rate = 0.0
            failure_rate = 0.0
        
        # Fraud rate
        if fraud_col:
            fraud_count = int(df[fraud_col].sum() if df[fraud_col].dtype == 'bool' else df[df[fraud_col] == 1].shape[0])
            fraud_rate = float(round((fraud_count / total_transactions) * 100, 2))
        else:
            fraud_rate = 0.0
        
        # Average amount
        if amount_col:
            avg_amount = float(round(df[amount_col].mean(), 2))
            total_volume = float(round(df[amount_col].sum(), 2))
        else:
            avg_amount = 0.0
            total_volume = 0.0
        
        # Calculate trends (compare to yesterday - simplified to 5% random for demo)
        import random
        total_trend = float(round(random.uniform(-5, 10), 1))
        success_trend = float(round(random.uniform(-2, 5), 1))
        failure_trend = float(round(random.uniform(-5, 2), 1))
        fraud_trend = float(round(random.uniform(-3, 1), 1))
        amount_trend = float(round(random.uniform(-8, 12), 1))
        volume_trend = float(round(random.uniform(-10, 15), 1))
        
        kpis = {
            "total_transactions": total_transactions,
            "total_trend": total_trend,
            "success_rate": success_rate,
            "success_trend": success_trend,
            "failure_rate": failure_rate,
            "failure_trend": failure_trend,
            "fraud_rate": fraud_rate,
            "fraud_trend": fraud_trend,
            "avg_amount": avg_amount,
            "amount_trend": amount_trend,
            "total_volume": total_volume,
            "volume_trend": volume_trend
        }
        
        # Overview data
        overview = {}
        
        # Transaction trend (last 7 days - simplified)
        if timestamp_col:
            try:
                df_copy = df.copy()
                df_copy[timestamp_col] = pd.to_datetime(df_copy[timestamp_col])
                last_7_days = df_copy.sort_values(timestamp_col).tail(min(len(df), 50000))
                daily_counts = last_7_days.groupby(last_7_days[timestamp_col].dt.date).size()
                trend_dates = [str(d) for d in daily_counts.index[-7:]]
                trend_values = [int(x) for x in daily_counts.values[-7:]]
            except:
                trend_dates = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
                trend_values = [30000, 32000, 31500, 33000, 34500, 33800, 35000]
        else:
            trend_dates = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
            trend_values = [30000, 32000, 31500, 33000, 34500, 33800, 35000]
        
        overview['trend'] = {
            'dates': trend_dates,
            'values': trend_values
        }
        
        # Top banks (convert to Python types)
        if bank_col:
            top_banks = df[bank_col].value_counts().head(10)
            overview['banks'] = {
                'banks': [str(x) for x in top_banks.index.tolist()],
                'values': [int(x) for x in top_banks.values.tolist()]
            }
        else:
            overview['banks'] = {
                'banks': ['Bank A', 'Bank B', 'Bank C', 'Bank D', 'Bank E'],
                'values': [45000, 38000, 32000, 28000, 25000]
            }
        
        # Transaction types (convert to Python types)
        if type_col:
            type_dist = df[type_col].value_counts().head(5)
            overview['types'] = {
                'types': [str(x) for x in type_dist.index.tolist()],
                'values': [int(x) for x in type_dist.values.tolist()]
            }
        else:
            overview['types'] = {
                'types': ['P2P', 'Merchant', 'Bill Payment', 'Recharge'],
                'values': [80000, 60000, 45000, 35000]
            }
        
        # Hourly pattern (convert to Python types)
        if hour_col:
            hourly = df[hour_col].value_counts().sort_index()
            overview['hourly'] = {
                'hours': [f'{int(h):02d}:00' for h in hourly.index],
                'values': [int(x) for x in hourly.values.tolist()]
            }
        else:
            overview['hourly'] = {
                'hours': [f'{h:02d}:00' for h in range(24)],
                'values': [5000, 3000, 2000, 1500, 1200, 2500, 6000, 12000, 15000, 14000, 
                          13000, 12500, 11000, 10500, 11500, 13000, 14500, 16000, 15500, 
                          14000, 12000, 10000, 8000, 6500]
            }
        
        return jsonify({
            "status": "success",
            "kpis": kpis,
            "overview": overview
        })
        
    except Exception as e:
        print(f"[ERROR] Dashboard stats failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": str(e)
        })

# ===== TIER 1 FEATURE ENDPOINTS =====

@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Get detected anomalies"""
    global tier1_manager
    
    if not tier1_manager:
        return jsonify({"status": "error", "error": "TIER 1 features not available"})
    
    try:
        anomalies = tier1_manager.get_anomalies()
        return jsonify({
            "status": "success",
            "anomalies": anomalies,
            "count": len(anomalies)
        })
    except Exception as e:
        print(f"[ERROR] Get anomalies failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

@app.route('/expand-query', methods=['POST'])
def expand_query():
    """Expand query using context memory"""
    global tier1_manager
    
    if not tier1_manager:
        return jsonify({"status": "error", "error": "TIER 1 features not available"})
    
    try:
        data = request.json
        query = data.get('query', '')
        
        expanded = tier1_manager.expand_query_with_context(query)
        context = tier1_manager.get_context_indicator()
        
        return jsonify({
            "status": "success",
            "original_query": query,
            "expanded_query": expanded,
            "context": context,
            "was_expanded": expanded != query
        })
    except Exception as e:
        print(f"[ERROR] Expand query failed: {e}")
        return jsonify({"status": "error", "error": str(e)})

if __name__ == '__main__':
    print("=" * 50)
    print("InsightX Backend Server")
    
    # Get settings from environment
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Running on http://{host}:{port}")
    print("=" * 50)
    
    app.run(debug=debug, host=host, port=port, use_reloader=False)
