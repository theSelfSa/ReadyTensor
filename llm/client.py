import json
import time
import logging
from typing import Dict, Any, Optional, Type, List
from openai import OpenAI
from pydantic import BaseModel
import tiktoken

logger = logging.getLogger(__name__)

class LLMClient:
    """Direct OpenAI API client replacing LangChain functionality"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", max_retries: int = 3):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")  # fallback
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        return len(self.encoding.encode(text))
    
    def invoke_structured(self, prompt: str, response_model: Type[BaseModel]) -> Dict[str, Any]:
        """Replace LangChain's structured output with direct OpenAI call"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0,
                    timeout=30
                )
                
                result_json = json.loads(response.choices[0].message.content)
                # Validate against Pydantic model
                validated = response_model(**result_json)
                return validated.model_dump()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to parse JSON response: {e}")
                
            except Exception as e:
                logger.error(f"API call failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def invoke(self, prompt: str) -> str:
        """Simple text completion"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    timeout=30
                )
                return response.choices[0].message.content
            
            except Exception as e:
                logger.error(f"API call failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)
    
    def validate_api_key(self) -> bool:
        """Test API key validity"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                timeout=10
            )
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
