"""
KnowledgeExplorer LLM Service
Groq wrapper with LangChain compatibility and streaming support
"""

import logging
from typing import Any, List, Optional, Iterator, Dict
import json
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

from backend_config import settings

logger = logging.getLogger(__name__)


class GroqLLM(LLM):
    """
    LangChain-compatible LLM wrapper for Groq API.
    
    This class implements the LangChain LLM interface, making it compatible
    with LangChain chains and agents.
    
    Debug tips:
    - Check GROQ_API_KEY is set in .env
    - Verify model name is valid (mixtral-8x7b-32768, llama2-70b-4096, etc.)
    - Monitor token usage in logs
    - Adjust temperature and max_tokens in .env for different behaviors
    """
    
    client: Any = None
    model: str = settings.groq_model
    temperature: float = settings.groq_temperature
    max_tokens: int = settings.groq_max_tokens
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        api_key = settings.groq_api_key
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        self.client = Groq(api_key=api_key)
        logger.info(f"✅ GroqLLM initialized with model: {self.model}")
    
    @property
    def _llm_type(self) -> str:
        """Return identifier for LLM type."""
        return "groq"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call Groq API with retry logic.
        
        Args:
            prompt: The prompt to send to the model
            stop: Optional list of stop sequences
            run_manager: Optional callback manager
            **kwargs: Additional arguments
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop,
            )
            
            content = response.choices[0].message.content
            logger.debug(f"Generated response: {len(content)} chars")
            return content
            
        except Exception as e:
            logger.error(f"❌ Groq API call failed: {e}")
            raise
    
    def stream_completion(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
    ) -> Iterator[str]:
        """
        Stream completion tokens from Groq API.
        
        Args:
            prompt: The prompt to send to the model
            stop: Optional list of stop sequences
            
        Yields:
            Token strings as they are generated
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stop=stop,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"❌ Groq streaming failed: {e}")
            raise


class LLMService:
    """
    High-level LLM service with SSE streaming helpers.
    
    This service provides methods for:
    - Standard completion
    - Token streaming with SSE formatting
    - RAG-optimized prompt templates
    """
    
    def __init__(self):
        try:
            self.llm = GroqLLM()
            self.available = True
        except Exception as e:
            logger.warning(f"⚠️  LLM service unavailable: {e}")
            self.available = False
            self.llm = None
    
    def build_rag_prompt(
        self,
        question: str,
        contexts: List[Dict[str, Any]],
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Build a RAG prompt with retrieved contexts.
        
        Args:
            question: User's question
            contexts: List of retrieved contexts with metadata
            system_instruction: Optional system instruction override
            
        Returns:
            Formatted prompt string
        """
        if system_instruction is None:
            system_instruction = (
                "You are a precise AI assistant that answers questions based on the provided context documents. "
                "Follow these rules:\n"
                "1. Use ONLY information from the context documents provided below\n"
                "2. Provide clear, natural, and well-structured answers\n"
                "3. Do NOT mention relevance scores or technical metadata in your answer\n"
                "4. Write in a professional and conversational tone\n"
                "5. If you cite sources, mention them naturally at the end like: 'Source: [filename]'\n"
                "6. If the context doesn't contain the answer, say so politely\n"
                "7. Do NOT include phrases like 'According to the document with relevance score...'"
            )
        
        # Format contexts WITHOUT relevance scores (internal use only)
        context_str = "\n\n---\n\n".join([
            f"[Document: {ctx.get('filename', 'unknown')}]\n{ctx.get('text', '')}"
            for i, ctx in enumerate(contexts)
        ])
        
        prompt = f"""{system_instruction}

=== CONTEXT DOCUMENTS ===
{context_str}

=== END OF CONTEXT ===

Question: {question}

Provide a clear, natural answer using only the information above. Do not mention relevance scores or technical details.

Answer:"""
        
        return prompt
    
    def build_general_prompt(self, question: str) -> str:
        """
        Build a prompt for general questions (no document context).
        
        Args:
            question: User's question
            
        Returns:
            Formatted prompt string
        """
        system_instruction = (
            "You are a helpful AI assistant. Answer the question clearly and accurately. "
            "Provide informative, well-structured responses."
        )
        
        prompt = f"""{system_instruction}

Question: {question}

Answer:"""
        
        return prompt
    
    def is_document_related_question(self, question: str) -> bool:
        """
        Detect if a question is asking about uploaded documents.
        
        Args:
            question: User's question
            
        Returns:
            True if question seems document-related, False otherwise
        """
        question_lower = question.lower()
        
        # Document-specific keywords
        document_keywords = [
            'document', 'file', 'pdf', 'upload', 'this', 'resume', 'report',
            'summarize', 'summary', 'what does', 'according to',
            'in the', 'from the', 'based on', 'mentioned', 'describe',
            'explain this', 'tell me about this', 'what is in',
            'information about', 'details about', 'content', 'paper'
        ]
        
        # Check if question contains document-related keywords
        return any(keyword in question_lower for keyword in document_keywords)
    
    def generate(self, prompt: str) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        if not self.available:
            raise RuntimeError("LLM service is not available")
        
        return self.llm._call(prompt)
    
    def stream_tokens(self, prompt: str) -> Iterator[str]:
        """
        Stream tokens for the given prompt.
        
        Args:
            prompt: Input prompt
            
        Yields:
            Token strings
        """
        if not self.available:
            raise RuntimeError("LLM service is not available")
        
        yield from self.llm.stream_completion(prompt)
    
    def format_sse_event(self, event_type: str, data: Any) -> str:
        """
        Format data as Server-Sent Event.
        
        Args:
            event_type: Event type (message, metadata, done, error)
            data: Data to send (will be JSON-encoded if dict)
            
        Returns:
            Formatted SSE string
        """
        if isinstance(data, dict):
            data_str = json.dumps(data)
        else:
            data_str = str(data)
        
        return f"event: {event_type}\ndata: {data_str}\n\n"
    
    def stream_sse_tokens(
        self,
        prompt: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Iterator[str]:
        """
        Stream tokens as SSE events.
        
        Args:
            prompt: Input prompt
            metadata: Optional metadata to send before streaming
            
        Yields:
            SSE-formatted event strings
        """
        try:
            # Send metadata if provided
            if metadata:
                yield self.format_sse_event("metadata", metadata)
            
            # Stream tokens
            full_response = []
            for token in self.stream_tokens(prompt):
                full_response.append(token)
                yield self.format_sse_event("message", token)
            
            # Send done event with full response
            yield self.format_sse_event("done", {
                "answer": "".join(full_response),
                "token_count": len(full_response)
            })
            
        except Exception as e:
            logger.error(f"❌ SSE streaming error: {e}")
            yield self.format_sse_event("error", {"error": str(e)})


# Global LLM service instance
llm_service = LLMService()
