"""
LLM Module - Language Model integration (OpenAI / Google Gemini)
"""
from typing import Optional, Dict, Any, List
import json
import re

from backend.config import settings


class LLMEngine:
    """
    LLM Engine supporting OpenAI and Google Gemini
    """
    
    def __init__(self):
        self.provider = settings.llm_provider.lower()
        self._client = None
        self._use_rest_api = False
        self.model_name = None
        self._demo_mode = False
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            self._client = OpenAI(api_key=settings.openai_api_key)
            print("✅ OpenAI client initialized")
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _init_gemini(self):
        """Initialize Google Gemini client - STRICT gemini-3-flash-preview ONLY"""
        import requests
        
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        
        # STRICT MODEL REQUIREMENT: gemini-3-flash-preview ONLY
        self.model_name = "gemini-3-flash-preview"
        self._use_rest_api = True  # Use REST API for reliability
        
        # Test the model
        test_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={settings.google_api_key}"
        test_data = {"contents": [{"parts": [{"text": "Hello"}]}]}
        
        try:
            response = requests.post(test_url, json=test_data, timeout=15)
            if response.status_code == 200:
                print(f"✅ Gemini 3 Flash Preview is ACTIVE and ready!")
                self._demo_mode = False
            else:
                print(f"❌ CRITICAL: gemini-3-flash-preview NOT AVAILABLE")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                print("⚠️ Entering DEMO MODE - Model requirement not met")
                self._demo_mode = True
                self.model_name = "demo-mode"
        except Exception as e:
            print(f"❌ CRITICAL: Failed to connect to Gemini API: {str(e)}")
            print("⚠️ Entering DEMO MODE")
            self._demo_mode = True
            self.model_name = "demo-mode"
    
    def generate(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text using the LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # Check for demo mode
        if hasattr(self, '_demo_mode') and self._demo_mode:
            return self._generate_demo(prompt)
        
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_gemini(prompt, system_prompt, temperature, max_tokens)
    
    def _generate_demo(self, prompt: str) -> str:
        """Generate demo responses when no API is available"""
        import json
        
        # Check if asking for questions
        if "question" in prompt.lower() or "generate" in prompt.lower():
            demo_questions = [
                {
                    "question": "Explain the core architecture of your project and the design patterns you used.",
                    "difficulty": "Medium",
                    "concepts": ["Architecture", "Design Patterns"]
                },
                {
                    "question": "What were the main challenges you faced during development and how did you overcome them?",
                    "difficulty": "Medium", 
                    "concepts": ["Problem Solving", "Development"]
                },
                {
                    "question": "Describe the database schema and why you chose this particular structure.",
                    "difficulty": "Hard",
                    "concepts": ["Database Design", "Data Modeling"]
                },
                {
                    "question": "How does your system handle error cases and edge scenarios?",
                    "difficulty": "Medium",
                    "concepts": ["Error Handling", "Edge Cases"]
                },
                {
                    "question": "What security measures have you implemented in your application?",
                    "difficulty": "Hard",
                    "concepts": ["Security", "Authentication"]
                }
            ]
            return json.dumps(demo_questions)
        
        # Check if evaluating an answer
        if "evaluate" in prompt.lower() or "score" in prompt.lower():
            return json.dumps({
                "score": 7,
                "feedback": "Good understanding demonstrated. Your explanation covers the key concepts well. Consider providing more specific examples to strengthen your answer.",
                "strengths": ["Clear explanation", "Good conceptual understanding"],
                "areas_for_improvement": ["Add more examples", "Discuss edge cases"]
            })
        
        # Default response
        return "This is a demo response. Please configure a valid Gemini API key for full functionality."
    
    def _generate_openai(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate using OpenAI"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def _generate_gemini(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate using Google Gemini"""
        # Check if using REST API fallback
        if self._use_rest_api:
            return self._generate_gemini_rest(prompt, system_prompt, temperature, max_tokens)
        
        # Use SDK
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        response = self._client.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def _generate_gemini_rest(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate using Gemini REST API (fallback)"""
        import requests
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={settings.google_api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                raise ValueError(f"Unexpected response format: {result}")
        else:
            raise ValueError(f"API request failed: {response.status_code} - {response.text}")
    
    def generate_json(
        self, 
        prompt: str, 
        system_prompt: str = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response
        
        Args:
            prompt: User prompt expecting JSON response
            system_prompt: System prompt
            temperature: Lower temperature for more consistent JSON
            
        Returns:
            Parsed JSON dictionary
        """
        response = self.generate(prompt, system_prompt, temperature)
        
        # Try to extract JSON from response
        try:
            # First try direct parsing
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # Return as dict with raw response
            return {"raw_response": response}


# Singleton instance
_llm_engine: Optional[LLMEngine] = None


def get_llm_engine() -> LLMEngine:
    """Get LLM engine instance"""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEngine()
    return _llm_engine
