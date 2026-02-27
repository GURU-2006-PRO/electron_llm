"""
Multi-LLM Service with DeepSeek R1 and Gemini
Supports model selection and better formatted responses
"""

from openai import OpenAI
import google.generativeai as genai
from threading import Thread
import uuid
import json
import time
import re

class MultiLLMService:
    def __init__(self, openrouter_key, gemini_key):
        """Initialize both DeepSeek (via OpenRouter) and Gemini"""
        
        # OpenRouter for DeepSeek
        self.openrouter_client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Gemini - Use Gemini 2.5 Flash (latest)
        genai.configure(api_key=gemini_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Available models
        self.MODELS = {
            "deepseek-chat": "deepseek/deepseek-chat",
            "deepseek-r1": "deepseek/deepseek-r1",
            "gemini-flash": "gemini-2.5-flash"
        }
        
        # Job storage for async processing
        self.jobs = {}
        
        # Query cache
        self.cache = {}
        
        # Query classification patterns
        self.SIMPLE_PATTERNS = [
            r'\b(what|show|list|display|get)\b.*\b(total|sum|count|average|mean|max|min|number)\b',
            r'\bhow many\b',
            r'\bhow much\b',
            r'\btotal\b.*\b(amount|transactions|records)\b',
            r'\baverage\b.*\b(amount|value|price)\b',
            r'\bcount\b.*\b(transactions|records|rows)\b',
            r'\bshow me\b.*\b(stats|statistics|numbers)\b',
            r'\b(highest|lowest|maximum|minimum)\b.*\b(value|amount)\b'
        ]
        
        self.COMPLEX_PATTERNS = [
            r'\b(analyze|analysis|examine|investigate|study)\b',
            r'\b(pattern|patterns|trend|trends|correlation)\b',
            r'\b(predict|prediction|forecast|estimate)\b',
            r'\b(why|explain|reason|cause|factor)\b.*\b(behind|for|of)\b',
            r'\b(compare|comparison|contrast|difference)\b.*\b(between|across)\b',
            r'\b(insight|insights|recommendation|recommendations)\b',
            r'\b(fraud|anomaly|anomalies|outlier|outliers)\b.*\b(detection|pattern)\b',
            r'\b(optimize|optimization|improve|improvement)\b',
            r'\b(relationship|relationships|correlation|correlations)\b',
            r'\b(segment|segmentation|cluster|clustering)\b',
            r'\b(impact|effect|influence)\b.*\b(on|of)\b',
            r'\bwhat if\b',
            r'\b(strategy|strategies|approach|approaches)\b'
        ]
        
        self.MODERATE_PATTERNS = [
            r'\b(summarize|summary|overview)\b',
            r'\b(breakdown|break down|distribution)\b',
            r'\b(group by|grouped by|by category|by type)\b',
            r'\b(top|bottom)\b.*\b(merchants|categories|states|banks)\b',
            r'\b(compare|comparison)\b(?!.*\b(pattern|trend|correlation)\b)',
            r'\b(filter|filtered|where)\b',
            r'\b(percentage|percent|proportion|ratio)\b'
        ]
        
        print("[OK] Multi-LLM service initialized (DeepSeek + Gemini 2.5 Flash)")
        print("[OK] Intelligent query classification enabled")
    
    def classify_query(self, query):
        """
        Classify query complexity and recommend best model
        
        Returns:
            str: 'gemini-flash', 'deepseek-chat', or 'deepseek-r1'
        """
        query_lower = query.lower()
        
        # Check for complex patterns first (most expensive)
        complex_score = sum(1 for pattern in self.COMPLEX_PATTERNS 
                          if re.search(pattern, query_lower, re.IGNORECASE))
        
        # Check for simple patterns (cheapest)
        simple_score = sum(1 for pattern in self.SIMPLE_PATTERNS 
                         if re.search(pattern, query_lower, re.IGNORECASE))
        
        # Check for moderate patterns (balanced)
        moderate_score = sum(1 for pattern in self.MODERATE_PATTERNS 
                           if re.search(pattern, query_lower, re.IGNORECASE))
        
        # Additional heuristics
        word_count = len(query.split())
        has_multiple_questions = query.count('?') > 1 or query.count(' and ') > 1
        
        # Decision logic
        if complex_score >= 2 or (complex_score >= 1 and word_count > 15):
            recommended = 'deepseek-r1'
            reason = 'Complex analysis requiring deep reasoning'
        elif simple_score >= 1 and complex_score == 0:
            recommended = 'gemini-flash'
            reason = 'Simple query - using free Gemini'
        elif moderate_score >= 1 or (word_count > 10 and complex_score == 0):
            recommended = 'deepseek-chat'
            reason = 'Moderate complexity - fast response'
        elif has_multiple_questions:
            recommended = 'deepseek-chat'
            reason = 'Multiple questions - balanced approach'
        else:
            # Default to free Gemini for unknown patterns
            recommended = 'gemini-flash'
            reason = 'Default to free model'
        
        print(f"[CLASSIFY] Query: '{query[:50]}...'")
        print(f"[CLASSIFY] Scores - Simple: {simple_score}, Moderate: {moderate_score}, Complex: {complex_score}")
        print(f"[CLASSIFY] Recommended: {recommended} ({reason})")
        
        return recommended, reason
    
    def query(self, user_query, data_context, model="auto"):
        """
        Query with specified model and automatic fallback
        
        Args:
            user_query: User's question
            data_context: Data summary
            model: "deepseek-chat", "deepseek-r1", "gemini-flash", or "auto" for classification
        """
        
        # Auto-classify if model is "auto"
        if model == "auto":
            model, reason = self.classify_query(user_query)
            print(f"[AUTO] Selected {model}: {reason}")
        
        # Check cache
        cache_key = f"{model}:{user_query}:{data_context[:100]}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            cached['from_cache'] = True
            return cached
        
        # Define fallback chain for OpenRouter models
        openrouter_fallback = [
            "deepseek-r1",
            "deepseek-chat",
            "anthropic/claude-3-haiku",  # Fast and cheap fallback
            "meta-llama/llama-3.1-8b-instruct"  # Free fallback
        ]
        
        # Try primary model
        result = self._try_model(user_query, data_context, model)
        
        # If primary model failed and it's an OpenRouter model, try fallbacks
        if result.get("type") == "error" and model in ["deepseek-r1", "deepseek-chat"]:
            print(f"[WARNING] {model} failed, trying fallbacks...")
            
            for fallback_model in openrouter_fallback:
                if fallback_model == model:
                    continue  # Skip the model that already failed
                
                print(f"[INFO] Trying fallback: {fallback_model}")
                result = self._try_model(user_query, data_context, fallback_model)
                
                if result.get("type") != "error":
                    result["fallback_used"] = True
                    result["original_model"] = model
                    result["actual_model"] = fallback_model
                    print(f"[OK] Fallback successful: {fallback_model}")
                    break
        
        return result
    
    def _try_model(self, user_query, data_context, model):
        """Try a specific model and return result"""
        print(f"[INFO] Trying model: {model}")
        
        try:
            # Route to appropriate model
            if model == "gemini-flash" or model == "gemini-pro":
                print(f"[INFO] Routing to Gemini API")
                return self._query_gemini(user_query, data_context)
            elif model == "deepseek-r1":
                print(f"[INFO] Routing to DeepSeek R1")
                return self._query_deepseek_r1(user_query, data_context)
            elif model == "deepseek-chat":
                print(f"[INFO] Routing to DeepSeek Chat")
                return self._query_deepseek_chat(user_query, data_context)
            else:
                # Generic OpenRouter model
                print(f"[INFO] Routing to OpenRouter: {model}")
                return self._query_openrouter_generic(user_query, data_context, model)
        except Exception as e:
            print(f"[ERROR] Model {model} failed: {e}")
            return {
                "error": str(e),
                "model": model,
                "type": "error"
            }
    
    def _query_gemini(self, query, context):
        """Query Gemini 2.5 Flash"""
        try:
            print(f"[INFO] Calling Gemini 2.5 Flash API...")
            start_time = time.time()
            
            prompt = f"""You are a data analyst. Analyze this transaction data and provide insights.

Data Context:
{context}

User Question: {query}

Provide a well-structured response with:
1. Direct answer
2. Key insights (bullet points)
3. Recommendations (if applicable)

Format your response clearly with sections."""

            response = self.gemini_model.generate_content(prompt)
            elapsed = time.time() - start_time
            
            print(f"[OK] Gemini response received in {elapsed:.2f}s")
            
            # Format response
            formatted = self._format_response(response.text)
            
            result = {
                "answer": formatted,
                "model": "gemini-flash",
                "type": "complete",
                "response_time": f"{elapsed:.2f}s",
                "from_cache": False
            }
            
            # Cache it
            cache_key = f"gemini-flash:{query}:{context[:100]}"
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Gemini API failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Gemini API error: {str(e)}",
                "model": "gemini-flash",
                "type": "error"
            }
    
    def _query_deepseek_chat(self, query, context):
        """Query DeepSeek Chat (fast)"""
        try:
            start_time = time.time()
            
            response = self.openrouter_client.chat.completions.create(
                model=self.MODELS["deepseek-chat"],
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a data analyst. Provide clear, structured responses.

Data Context:
{context}

Format your response with:
- Direct answer first
- Key insights as bullet points
- Use numbers and statistics
- Be concise but informative"""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            elapsed = time.time() - start_time
            answer = response.choices[0].message.content
            
            # Format response
            formatted = self._format_response(answer)
            
            result = {
                "answer": formatted,
                "model": "deepseek-chat",
                "type": "complete",
                "response_time": f"{elapsed:.2f}s",
                "from_cache": False
            }
            
            # Cache it
            cache_key = f"deepseek-chat:{query}:{context[:100]}"
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "model": "deepseek-chat",
                "type": "error"
            }
    
    def _query_deepseek_r1(self, query, context):
        """Query DeepSeek R1 with progressive enhancement"""
        
        # Step 1: Quick answer with chat model
        quick_result = self._query_deepseek_chat(query, context)
        
        if "error" in quick_result:
            return quick_result
        
        # Step 2: Start deep reasoning in background
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "status": "processing",
            "quick_answer": quick_result["answer"]
        }
        
        # Start background thread for R1 reasoning
        thread = Thread(
            target=self._deep_reasoning_r1,
            args=(job_id, query, context, quick_result["answer"])
        )
        thread.daemon = True
        thread.start()
        
        return {
            "answer": quick_result["answer"],
            "model": "deepseek-r1",
            "type": "progressive",
            "job_id": job_id,
            "message": "Getting deeper insights with DeepSeek R1...",
            "response_time": quick_result["response_time"]
        }
    
    def _deep_reasoning_r1(self, job_id, query, context, quick_answer):
        """Deep reasoning with DeepSeek R1 (background)"""
        try:
            start_time = time.time()
            
            response = self.openrouter_client.chat.completions.create(
                model=self.MODELS["deepseek-r1"],
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert data analyst with deep reasoning capabilities.

Data Context:
{context}

Initial Quick Answer:
{quick_answer}

Now provide a comprehensive analysis with:
1. Detailed insights
2. Hidden patterns and correlations
3. Statistical significance
4. Actionable recommendations
5. Potential risks or opportunities

Use clear formatting with sections and bullet points."""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            elapsed = time.time() - start_time
            
            # Format response
            formatted = self._format_response(response.choices[0].message.content)
            
            self.jobs[job_id] = {
                "status": "complete",
                "enhanced_answer": formatted,
                "model": "deepseek-r1",
                "response_time": f"{elapsed:.2f}s"
            }
            
        except Exception as e:
            self.jobs[job_id] = {
                "status": "error",
                "error": str(e)
            }
    
    def _format_response(self, text):
        """Format response for better readability with HTML"""
        
        # Remove excessive asterisks used for emphasis
        text = re.sub(r'\*{2,}', '', text)
        
        # Convert markdown headers to HTML
        text = re.sub(r'###\s+(.+)', r'<h3>\1</h3>', text)
        text = re.sub(r'##\s+(.+)', r'<h2>\1</h2>', text)
        text = re.sub(r'#\s+(.+)', r'<h1>\1</h1>', text)
        
        # Convert numbered lists to HTML
        lines = text.split('\n')
        formatted_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                if in_list:
                    formatted_lines.append('</ol>')
                    in_list = False
                formatted_lines.append('<br>')
                continue
            
            # Numbered list items
            if re.match(r'^\d+[\.\)]\s+', line):
                if not in_list:
                    formatted_lines.append('<ol>')
                    in_list = True
                item = re.sub(r'^\d+[\.\)]\s+', '', line)
                formatted_lines.append(f'<li>{item}</li>')
            
            # Bullet points
            elif re.match(r'^[\-\•\*]\s+', line):
                if in_list:
                    formatted_lines.append('</ol>')
                    in_list = False
                item = re.sub(r'^[\-\•\*]\s+', '', line)
                formatted_lines.append(f'<div class="bullet-point">• {item}</div>')
            
            # Section headers (words followed by colon)
            elif re.match(r'^([A-Z][^:]+):\s*$', line):
                if in_list:
                    formatted_lines.append('</ol>')
                    in_list = False
                formatted_lines.append(f'<div class="section-header">{line}</div>')
            
            # Regular text
            else:
                if in_list:
                    formatted_lines.append('</ol>')
                    in_list = False
                formatted_lines.append(f'<p>{line}</p>')
        
        if in_list:
            formatted_lines.append('</ol>')
        
        return '\n'.join(formatted_lines)
    
    def get_job_status(self, job_id):
        """Get status of background reasoning job"""
        return self.jobs.get(job_id, {"status": "not_found"})
    
    def clear_cache(self):
        """Clear query cache"""
        self.cache.clear()
        return {"message": "Cache cleared"}
    
    def _query_openrouter_generic(self, query, context, model_name):
        """Generic OpenRouter query for fallback models"""
        try:
            start_time = time.time()
            
            response = self.openrouter_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a data analyst. Provide clear, structured responses.

Data Context:
{context}

Format your response with:
- Direct answer first
- Key insights as bullet points
- Use numbers and statistics
- Be concise but informative"""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            elapsed = time.time() - start_time
            answer = response.choices[0].message.content
            
            # Format response
            formatted = self._format_response(answer)
            
            result = {
                "answer": formatted,
                "model": model_name,
                "type": "complete",
                "response_time": f"{elapsed:.2f}s",
                "from_cache": False
            }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "model": model_name,
                "type": "error"
            }
    
    def get_available_models(self):
        """Get list of available models"""
        return {
            "models": [
                {
                    "id": "deepseek-chat",
                    "name": "DeepSeek Chat",
                    "description": "Fast responses (1-2s)",
                    "best_for": "Quick queries, simple analysis"
                },
                {
                    "id": "deepseek-r1",
                    "name": "DeepSeek R1",
                    "description": "Deep reasoning (10-30s)",
                    "best_for": "Complex analysis, insights, recommendations"
                },
                {
                    "id": "gemini-flash",
                    "name": "Google Gemini 2.5 Flash",
                    "description": "Fast & balanced (2-5s)",
                    "best_for": "General analysis, varied queries"
                }
            ]
        }
