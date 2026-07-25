"""EmergentLLM Client for CloudGuardian using Emergent Universal Key"""

import os
import logging
from typing import Dict, List, Optional
from emergentintegrations import EmergentAI

logger = logging.getLogger(__name__)

class EmergentLLMClient:
    """
    LLM client using Emergent Universal Key
    Supports GPT-5.2 (OpenAI) and Claude Sonnet 4.6 (Anthropic)
    """
    
    def __init__(self, provider: str = 'gpt-5.2', temperature: float = 0.3):
        """
        Initialize Emergent LLM client
        
        Args:
            provider: 'gpt-5.2' or 'claude-sonnet-4.6'
            temperature: Creativity parameter (0.0-1.0)
        """
        self.provider = provider
        self.temperature = temperature
        
        # Initialize Emergent AI client (Universal Key loaded automatically)
        self.client = EmergentAI()
        
        logger.info(f"Initialized EmergentLLMClient with provider: {provider}")
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> Dict:
        """
        Generate LLM response
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum response length
        
        Returns:
            Dict with 'content', 'model', 'usage'
        """
        try:
            if self.provider == 'gpt-5.2':
                response = self.client.chat.completions.create(
                    model="gpt-5.2",
                    messages=[
                        {"role": "system", "content": "You are a cloud security expert specializing in AWS remediation."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                
                return {
                    'content': response.choices[0].message.content,
                    'model': 'gpt-5.2',
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
            
            elif self.provider == 'claude-sonnet-4.6':
                response = self.client.messages.create(
                    model="claude-sonnet-4.6",
                    system="You are a cloud security expert specializing in AWS remediation.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=max_tokens
                )
                
                return {
                    'content': response.content[0].text,
                    'model': 'claude-sonnet-4.6',
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens
                    }
                }
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def generate_with_retry(self, prompt: str, max_retries: int = 3) -> Dict:
        """
        Generate with automatic retry on failure
        """
        for attempt in range(max_retries):
            try:
                return self.generate(prompt)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {e}")
                continue
