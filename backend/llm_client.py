"""
LLM Service with OpenRouter API
Supports DeepSeek R1 with progressive enhancement
"""

from openai import OpenAI
from threading import Thread
import uuid
import json
import time

class LLMService:
    def __init__(self, api_key):
        """Initialize OpenRouter client"""
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Model configurations
        self.FAST_MODEL = "deepseek/deepseek-chat"  # Fast, 1-2 seconds
        self.REASONING_MODEL = "deepseek/deepseek-r1"  # Reasoning, 10-30 seconds
        
        # Job storage for async processing
        self.jobs = {}
        
        # Query cache for repeated queries
        self.cache = {}
    
    def query(self, user_query, data_context, use_reasoning=None):
        """
        Smart query processing with automatic model selection
        
        Args:
            user_query: User's natural language query
            data_context: Data summary/context for the model
            use_reasoning: Force reasoning model (True/False/None for auto)
        
        Returns:
            dict with answer and metadata
        """
        
        # Check cache first
        cache_key = f"{user_query}:{data_context[:100]}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            cached['from_cache'] = True
            return cached
        
        # Auto-detect if reasoning is needed
        if use_reasoning is None:
            use_reasoning = self._needs_reasoning(user_query)
        
        if use_reasoning:
            # Complex query - use progressive enhancement
            return self._progressive_query(user_query, data_context)
        else:
            # Simple query - fast model only
            return self._fast_query(user_query, data_context)
    
    def _needs_reasoning(self, query):
        """Determine if query needs deep reasoning"""
        reasoning_keywords = [
            'why', 'analyze', 'explain', 'predict', 'recommend',
            'insight', 'trend', 'pattern', 'correlation', 'cause',
            'impact', 'effect', 'relationship', 'compare', 'contrast'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in reasoning_keywords)
    
    def _fast_query(self, query, context):
        """Fast response using DeepSeek Chat (1-2 seconds)"""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.FAST_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a data analyst. Analyze this data context:\n{context}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            elapsed = time.time() - start_time
            answer = response.choices[0].message.content
            
            result = {
                "answer": answer,
                "model": self.FAST_MODEL,
                "type": "fast",
                "response_time": f"{elapsed:.2f}s",
                "from_cache": False
            }
            
            # Cache the result
            cache_key = f"{query}:{context[:100]}"
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "type": "error"
            }
    
    def _progressive_query(self, query, context):
        """Progressive enhancement: Fast answer + Deep reasoning"""
        
        # Step 1: Get quick answer first
        quick_result = self._fast_query(query, context)
        
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
            target=self._deep_reasoning,
            args=(job_id, query, context, quick_result["answer"])
        )
        thread.daemon = True
        thread.start()
        
        return {
            "answer": quick_result["answer"],
            "model": self.FAST_MODEL,
            "type": "progressive",
            "job_id": job_id,
            "message": "Getting deeper insights with DeepSeek R1...",
            "response_time": quick_result["response_time"]
        }
    
    def _deep_reasoning(self, job_id, query, context, quick_answer):
        """Deep reasoning with DeepSeek R1 (runs in background)"""
        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.REASONING_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert data analyst with deep reasoning capabilities.
                        
Data Context:
{context}

Initial Quick Answer:
{quick_answer}

Now provide a deeper, more comprehensive analysis with:
1. Detailed insights
2. Hidden patterns
3. Actionable recommendations
4. Statistical significance
"""
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
            
            self.jobs[job_id] = {
                "status": "complete",
                "enhanced_answer": response.choices[0].message.content,
                "model": self.REASONING_MODEL,
                "response_time": f"{elapsed:.2f}s",
                "reasoning_tokens": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
        except Exception as e:
            self.jobs[job_id] = {
                "status": "error",
                "error": str(e)
            }
    
    def get_job_status(self, job_id):
        """Get status of background reasoning job"""
        return self.jobs.get(job_id, {"status": "not_found"})
    
    def clear_cache(self):
        """Clear query cache"""
        self.cache.clear()
        return {"message": "Cache cleared"}
