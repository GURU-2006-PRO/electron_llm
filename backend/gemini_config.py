"""
Gemini Model Configuration
Manages 3 Gemini API keys with different models
"""

import google.generativeai as genai

class GeminiManager:
    def __init__(self, key_3_flash, key_2_5_flash_1, key_2_5_flash_2):
        """Initialize with 3 Gemini API keys"""
        self.models = {
            'gemini-3-flash': {
                'key': key_3_flash,
                'model_name': 'gemini-3-flash-preview',
                'display_name': 'Gemini 3.0 Flash Preview',
                'limit': '20 req/day',
                'model_instance': None
            },
            'gemini-2.5-flash-1': {
                'key': key_2_5_flash_1,
                'model_name': 'gemini-2.0-flash-exp',
                'display_name': 'Gemini 2.5 Flash (Key 1)',
                'limit': '1500 req/day',
                'model_instance': None
            },
            'gemini-2.5-flash-2': {
                'key': key_2_5_flash_2,
                'model_name': 'gemini-2.0-flash-exp',
                'display_name': 'Gemini 2.5 Flash (Key 2)',
                'limit': '1500 req/day',
                'model_instance': None
            }
        }
        
        # Initialize all models
        for model_id, config in self.models.items():
            if not config['key'] or config['key'] == '':
                print(f"[SKIP] {config['display_name']} - no API key provided")
                continue
                
            try:
                genai.configure(api_key=config['key'])
                config['model_instance'] = genai.GenerativeModel(config['model_name'])
                print(f"[OK] {config['display_name']} initialized ({config['limit']})")
            except Exception as e:
                print(f"[ERROR] Failed to initialize {config['display_name']}: {e}")
    
    def get_model(self, model_id='gemini-3-flash'):
        """Get a specific Gemini model instance"""
        if model_id not in self.models:
            model_id = 'gemini-3-flash'  # Default
        
        config = self.models[model_id]
        
        # Check if key exists
        if not config['key'] or config['key'] == '':
            raise Exception(f"No API key configured for {config['display_name']}")
        
        # Check if model was initialized
        if config['model_instance'] is None:
            raise Exception(f"{config['display_name']} not initialized - invalid API key")
        
        # Reconfigure with the correct key before returning
        genai.configure(api_key=config['key'])
        
        return config['model_instance'], config['display_name']
    
    def get_available_models(self):
        """Get list of available models for frontend"""
        return [
            {
                'id': model_id,
                'name': config['display_name'],
                'limit': config['limit']
            }
            for model_id, config in self.models.items()
        ]
