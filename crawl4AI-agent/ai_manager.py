#!/usr/bin/env python3
"""
AI Manager Module - The intelligent coordinator for the clinic AI assistant.

This module acts as the "brain" that decides when to use:
1. RAG (Retrieval Augmented Generation) for clinic-specific information
2. Web search for current/recent information not in the knowledge base

The manager first tries RAG, then intelligently determines if web search is needed.
"""

import asyncio
import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart

from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps
from web_search import WebSearcher
import os


@dataclass
class AIManagerDeps:
    """Dependencies for the AI Manager"""
    clinic_deps: ClinicAIDeps
    web_searcher: WebSearcher


class AIManager:
    """
    Intelligent AI Manager that coordinates between RAG and web search.
    
    This manager:
    1. First attempts to answer using clinic RAG data
    2. Analyzes if the response indicates need for current/web information
    3. Performs web search if needed and synthesizes final answer
    """
    
    def __init__(self):
        self.web_searcher = WebSearcher()
        
        # Keywords that suggest current/recent information might be needed
        self.current_info_keywords = [
            "latest", "recent", "current", "new", "updated", "2024", "2025", 
            "now", "today", "this year", "trending", "modern", "newest",
            "price", "cost", "availability", "schedule", "appointment",
            "comparison", "versus", "vs", "alternative", "competitor"
        ]
        
        # Phrases that indicate the AI needs web search
        self.web_search_indicators = [
            "i don't have current information",
            "i cannot find specific information",
            "for the most up-to-date",
            "contact the clinic directly",
            "i don't have information about",
            "not available in my knowledge",
            "current pricing",
            "latest information",
            "recent developments"
        ]
    
    async def process_query(
        self, 
        user_query: str, 
        deps: AIManagerDeps,
        message_history: Optional[List] = None
    ) -> ModelResponse:
        """
        Process a user query by intelligently coordinating RAG and web search.
        
        Args:
            user_query: The user's question
            deps: Dependencies including clinic deps and web searcher
            message_history: Previous conversation history
            
        Returns:
            ModelResponse with the final answer
        """
        
        # Step 1: Try RAG first
        rag_result = await self._get_rag_response(user_query, deps.clinic_deps, message_history)
        rag_text = rag_result.data if hasattr(rag_result, 'data') else str(rag_result)
        
        # Step 2: Analyze if web search is needed
        needs_web_search = self._analyze_need_for_web_search(user_query, rag_text)
        
        if not needs_web_search:
            # RAG response is sufficient
            return rag_result
        
        # Step 3: Perform web search for additional information
        web_search_query = self._create_web_search_query(user_query, rag_text)
        web_results = await self.web_searcher.search_web(web_search_query, max_results=3)
        formatted_web_results = self.web_searcher.format_search_results(web_results)
        
        # Step 4: Synthesize final answer combining RAG and web search
        final_response = await self._synthesize_final_answer(
            user_query, rag_text, formatted_web_results, deps.clinic_deps, message_history
        )
        
        return final_response
    
    async def _get_rag_response(
        self, 
        user_query: str, 
        clinic_deps: ClinicAIDeps,
        message_history: Optional[List] = None
    ) -> ModelResponse:
        """Get response using only RAG (clinic knowledge base)."""
        try:
            if message_history:
                result = await clinic_ai_expert.run(user_query, deps=clinic_deps, message_history=message_history)
            else:
                result = await clinic_ai_expert.run(user_query, deps=clinic_deps)
            return result
        except Exception as e:
            print(f"Error in RAG response: {e}")
            return ModelResponse(parts=[TextPart(content=f"Error retrieving clinic information: {str(e)}")])
    
    def _analyze_need_for_web_search(self, user_query: str, rag_response: str) -> bool:
        """
        Analyze if web search is needed based on the query and RAG response.
        
        Args:
            user_query: Original user question
            rag_response: Response from RAG system
            
        Returns:
            True if web search should be performed
        """
        query_lower = user_query.lower()
        response_lower = rag_response.lower()
        
        # Check if query contains keywords suggesting current information needed
        query_needs_current = any(keyword in query_lower for keyword in self.current_info_keywords)
        
        # Check if response indicates limited information
        response_indicates_search = any(indicator in response_lower for indicator in self.web_search_indicators)
        
        # Additional checks
        short_response = len(rag_response.strip()) < 200  # Very short responses might need supplementing
        no_specific_info = "no relevant clinic information found" in response_lower
        
        return query_needs_current or response_indicates_search or short_response or no_specific_info
    
    def _create_web_search_query(self, original_query: str, rag_response: str) -> str:
        """
        Create an optimized search query for web search.
        
        Args:
            original_query: User's original question
            rag_response: Response from RAG system
            
        Returns:
            Optimized search query
        """
        # Extract key terms from the original query
        query_lower = original_query.lower()
        
        # Base search terms
        search_terms = []
        
        # Add treatment/procedure specific terms
        if any(term in query_lower for term in ["botox", "filler", "laser", "treatment"]):
            # Keep medical terms
            search_terms.append("aesthetic medicine")
        
        # Add temporal context for current information
        if any(term in query_lower for term in ["price", "cost", "latest", "current", "new"]):
            search_terms.append("2024")
        
        # Create search query
        if "price" in query_lower or "cost" in query_lower:
            search_query = f"{original_query} Germany aesthetic clinic pricing 2024"
        elif "latest" in query_lower or "new" in query_lower:
            search_query = f"{original_query} latest developments 2024"
        else:
            search_query = f"{original_query} aesthetic medicine Germany"
        
        return search_query
    
    async def _synthesize_final_answer(
        self,
        user_query: str,
        rag_response: str,
        web_results: str,
        clinic_deps: ClinicAIDeps,
        message_history: Optional[List] = None
    ) -> ModelResponse:
        """
        Synthesize final answer combining RAG and web search results.
        
        Args:
            user_query: Original user question
            rag_response: Response from clinic RAG
            web_results: Formatted web search results
            clinic_deps: Clinic dependencies
            message_history: Conversation history
            
        Returns:
            Final synthesized response
        """
        
        synthesis_prompt = f"""
Based on the user's question: "{user_query}"

I have two sources of information:

1. CLINIC KNOWLEDGE (from Haut Labor Oldenburg database):
{rag_response}

2. CURRENT WEB INFORMATION:
{web_results}

CRITICAL INSTRUCTIONS:
- Do NOT fabricate, invent, or hallucinate any studies, research papers, or specific sources
- Do NOT create fake URLs, website names, or publication citations
- If you don't have specific information, clearly state this limitation
- Only reference information that is explicitly provided in the sources above
- Be honest about what information is available vs. what is not

Please provide a comprehensive answer that:
- Prioritizes our clinic's specific information and services
- Supplements with general information from web search where helpful
- Maintains focus on Haut Labor Oldenburg clinic
- Provides actionable advice for the user
- Includes clinic contact information when appropriate
- Always recommends consulting with qualified medical professionals

If there are discrepancies between sources, prioritize clinic-specific information but mention general industry information when relevant.
"""
        
        try:
            if message_history:
                result = await clinic_ai_expert.run(synthesis_prompt, deps=clinic_deps, message_history=message_history)
            else:
                result = await clinic_ai_expert.run(synthesis_prompt, deps=clinic_deps)
            return result
        except Exception as e:
            print(f"Error in synthesis: {e}")
            # Fallback: return original RAG response with web info appended
            combined_response = f"{rag_response}\n\n**Additional Current Information:**\n{web_results}"
            return ModelResponse(parts=[TextPart(content=combined_response)])


# Convenience functions for easy integration
async def process_clinic_query(
    user_query: str,
    clinic_deps: ClinicAIDeps,
    message_history: Optional[List] = None
) -> ModelResponse:
    """
    Convenience function to process a clinic query using the AI Manager.
    
    Args:
        user_query: The user's question
        clinic_deps: Clinic dependencies (Supabase, OpenAI client)
        message_history: Previous conversation history
        
    Returns:
        ModelResponse with the processed answer
    """
    manager = AIManager()
    web_searcher = WebSearcher()
    
    deps = AIManagerDeps(
        clinic_deps=clinic_deps,
        web_searcher=web_searcher
    )
    
    return await manager.process_query(user_query, deps, message_history)


# Test function
async def test_manager():
    """Test the AI Manager functionality."""
    from supabase import create_client
    from openai import AsyncOpenAI
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Setup test dependencies
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )
    openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    clinic_deps = ClinicAIDeps(supabase=supabase, openai_client=openai_client)
    
    # Test queries
    test_queries = [
        "What is the latest price for Botox treatments?",  # Should trigger web search
        "Tell me about Dr. Larisa Pfahl",  # Should use only RAG
        "What are the newest aesthetic treatments available in 2024?"  # Should trigger web search
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: {query}")
        print("-" * 50)
        
        result = await process_clinic_query(query, clinic_deps)
        print(f"📝 Response: {result.data if hasattr(result, 'data') else str(result)}")


if __name__ == "__main__":
    asyncio.run(test_manager())