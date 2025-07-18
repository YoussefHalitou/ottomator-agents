#!/usr/bin/env python3
"""
Web search module for clinic AI assistant
Provides web search capabilities with medical disclaimers and safety features.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import httpx
import json
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class WebSearcher:
    """Web search client with Tavily and DuckDuckGo support"""
    
    def __init__(self):
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using Tavily API or fallback methods
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, content
        """
        
        # Add medical disclaimer keywords for medical queries
        if any(keyword in query.lower() for keyword in ['botox', 'filler', 'treatment', 'medical', 'aesthetic']):
            query += " clinical evidence medical research"
        
        try:
            # Try Tavily API first if available
            if self.tavily_api_key:
                results = await self._search_tavily(query, max_results)
                if results:
                    logger.info(f"Tavily search returned {len(results)} results")
                    return results
            
            # Fallback to web scraping search
            results = await self._search_web_scrape(query, max_results)
            if results:
                logger.info(f"Web scrape search returned {len(results)} results")
                return results
                
            # Last resort: return helpful message
            return [{
                'title': 'Web Search Information',
                'url': 'https://www.ncbi.nlm.nih.gov/pubmed/',
                'content': f'For medical research on "{query}", please consult PubMed or speak with a qualified medical professional. This AI assistant cannot provide medical advice.'
            }]
            
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return [{
                'title': 'Search Error - Medical Disclaimer',
                'url': 'https://www.ncbi.nlm.nih.gov/pubmed/',
                'content': 'Web search is temporarily unavailable. For medical research, please consult PubMed, medical databases, or qualified healthcare professionals.'
            }]
    
    async def _search_tavily(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        try:
            response = await self.client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": max_results,
                    "include_answer": True,
                    "include_domains": ["pubmed.ncbi.nlm.nih.gov", "scholar.google.com", "clinicaltrials.gov"]
                }
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for result in data.get("results", []):
                results.append({
                    'title': result.get('title', 'No title'),
                    'url': result.get('url', ''),
                    'content': result.get('content', result.get('snippet', ''))
                })
            
            return results
            
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
            return []
    
    async def _search_web_scrape(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Fallback web search using search engines"""
        try:
            # Use a public search API or scraping service
            # For this example, I'll use a simple approach
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            response = await self.client.get(search_url)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Check RelatedTopics for results
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'title': topic.get('Text', '')[:100] + '...',
                        'url': topic.get('FirstURL', ''),
                        'content': topic.get('Text', '')
                    })
            
            # Also check AbstractText
            if data.get("AbstractText") and len(results) < max_results:
                results.append({
                    'title': f"Overview: {query}",
                    'url': data.get("AbstractURL", ""),
                    'content': data.get("AbstractText", "")
                })
            
            return results
            
        except Exception as e:
            logger.warning(f"Web scrape search failed: {e}")
            return []
    
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for AI consumption"""
        if not results:
            return "No search results found. Please consult medical databases or healthcare professionals for medical information."
        
        formatted = "## Web Search Results\n\n"
        formatted += "⚠️ **Medical Disclaimer**: These are search results from the internet. Always consult qualified healthcare professionals for medical advice.\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')[:100]
            url = result.get('url', 'No URL')
            content = result.get('content', 'No content')[:300]
            
            formatted += f"### Result {i}: {title}\n"
            formatted += f"**Source**: {url}\n"
            formatted += f"**Content**: {content}...\n\n"
        
        formatted += "\n---\n"
        formatted += "**Important**: Always verify medical information with qualified healthcare professionals and peer-reviewed sources."
        
        return formatted
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Global instance
_searcher = None

async def get_searcher() -> WebSearcher:
    """Get or create global searcher instance"""
    global _searcher
    if _searcher is None:
        _searcher = WebSearcher()
    return _searcher

async def search_web(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for web search"""
    searcher = await get_searcher()
    return await searcher.search_web(query, max_results)

if __name__ == "__main__":
    async def test():
        searcher = WebSearcher()
        results = await searcher.search_web("Botox effectiveness studies")
        print(searcher.format_search_results(results))
        await searcher.close()
    
    asyncio.run(test())