"""
Direct OpenAI API client with .env configuration support
"""

import json
import time
import logging
from typing import Dict, Any, Type
from openai import OpenAI
from pydantic import BaseModel
import tiktoken

logger = logging.getLogger(__name__)

class LLMClient:
    """Direct OpenAI client with enhanced configuration"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("API key is required")
            
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # Initialize tokenizer
        try:
            self.encoding = tiktoken.encoding_for_model(model)
            logger.info(f"Initialized tokenizer for model: {model}")
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Using fallback tokenizer for model: {model}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not text:
            return 0
        return len(self.encoding.encode(str(text)))
    
    def validate_api_key(self) -> bool:
        """Test API key validity"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1,
                timeout=10
            )
            logger.info("API key validation successful")
            return True
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
    
    def invoke_structured(self, prompt: str, response_model: Type[BaseModel]) -> Dict[str, Any]:
        """Structured output generation with retry logic"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    temperature=0,
                    timeout=60
                )
                
                # Parse and validate response
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from API")
                
                result_json = json.loads(content)
                validated = response_model(**result_json)
                
                logger.debug(f"Structured API call successful (attempt {attempt + 1})")
                return validated.model_dump()
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse JSON response after {max_retries} attempts")
                    
            except Exception as e:
                logger.error(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def invoke(self, prompt: str) -> str:
        """Simple text completion"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    timeout=60
                )
                
                content = response.choices[0].message.content
                if not content:
                    raise ValueError("Empty response from API")
                
                logger.debug(f"Text API call successful (attempt {attempt + 1})")
                return content
                
            except Exception as e:
                logger.error(f"API call failed (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)
