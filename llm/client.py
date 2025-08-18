# ReadyTensor/llm/client.py

import json
import logging
from typing import Dict, Any, Type
from openai import OpenAI
from pydantic import BaseModel
import tiktoken

logger = logging.getLogger(__name__)

class LLMClient:
    """Direct OpenAI client with no retries (development mode)"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("API key is required")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
            logger.info(f"Initialized tokenizer for model: {model}")
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"Using fallback tokenizer for model: {model}")

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(str(text))) if text else 0

    def validate_api_key(self) -> bool:
        try:
            self.client.chat.completions.create(
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
        """Structured output generation without retries"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
            timeout=60
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from API")
        result_json = json.loads(content)
        validated = response_model(**result_json)
        return validated.model_dump()

    def invoke(self, prompt: str) -> str:
        """Simple text completion without retries"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=60
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from API")
        return content
