#!/usr/bin/env python3
"""
Web Search Module for retrieving current information from the internet.
This module handles web searches when the AI needs current/recent information.
"""

import os
import httpx
import asyncio
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

load_dotenv()


class WebSearcher:
    """
    A web search client that can perform searches for current information.
    Uses Tavily API for high-quality search results.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.base_url = "https://api.tavily.com"
        
    async def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Perform a web search and return relevant results.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, content, and URL
        """
        if not self.api_key:
            # Fallback to a simple HTTP search if no API key
            return await self._fallback_search(query, max_results)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    json={
                        "api_key": self.api_key,
                        "query": query,
                        "search_depth": "basic",
                        "include_answer": True,
                        "include_raw_content": False,
                        "max_results": max_results,
                        "include_domains": [],
                        "exclude_domains": []
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Add the direct answer if available
                    if data.get("answer"):
                        results.append({
                            "title": "Direct Answer",
                            "content": data["answer"],
                            "url": "Multiple sources",
                            "score": 1.0
                        })
                    
                    # Add search results
                    for result in data.get("results", []):
                        results.append({
                            "title": result.get("title", ""),
                            "content": result.get("content", ""),
                            "url": result.get("url", ""),
                            "score": result.get("score", 0.5)
                        })
                    
                    return results
                else:
                    print(f"Tavily API error: {response.status_code}")
                    return await self._fallback_search(query, max_results)
                    
        except Exception as e:
            print(f"Web search error: {e}")
            return await self._fallback_search(query, max_results)
    
    async def _fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """
        Fallback search method when main API is unavailable.
        Uses DuckDuckGo instant answers or similar free service.
        """
        try:
            async with httpx.AsyncClient() as client:
                # Try DuckDuckGo instant answers
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    # Add abstract if available
                    if data.get("Abstract"):
                        results.append({
                            "title": f"Information about: {query}",
                            "content": data["Abstract"],
                            "url": data.get("AbstractURL", "DuckDuckGo"),
                            "score": 0.8
                        })
                    
                    # Add definition if available
                    if data.get("Definition"):
                        results.append({
                            "title": f"Definition: {query}",
                            "content": data["Definition"],
                            "url": data.get("DefinitionURL", "DuckDuckGo"),
                            "score": 0.7
                        })
                    
                    # Add related topics
                    for topic in data.get("RelatedTopics", [])[:max_results-len(results)]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            results.append({
                                "title": "Related Information",
                                "content": topic["Text"],
                                "url": topic.get("FirstURL", ""),
                                "score": 0.6
                            })
                    
                    return results
                    
        except Exception as e:
            print(f"Fallback search error: {e}")
        
        # Final fallback - return a message indicating search unavailable
        return [{
            "title": "Web Search Unavailable",
            "content": f"I cannot search the web for current information about '{query}' at the moment. Please contact the clinic directly for the most up-to-date information at +49 (0) 157 834 488 90 or info@haut-labor.de.",
            "url": "",
            "score": 0.1
        }]
    
    def format_search_results(self, results: List[Dict]) -> str:
        """
        Format search results into a readable string for the AI.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string with all search results
        """
        if not results:
            return "No search results found."
        
        formatted_results = ["## Web Search Results\n"]
        
        for i, result in enumerate(results, 1):
            formatted_results.append(f"### Result {i}: {result['title']}")
            formatted_results.append(f"**Source:** {result['url']}")
            formatted_results.append(f"**Content:** {result['content']}")
            formatted_results.append("---\n")
        
        return "\n".join(formatted_results)


# Convenience function for easy import
async def search_web(query: str, max_results: int = 5) -> str:
    """
    Convenience function to perform a web search and return formatted results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        Formatted string with search results
    """
    searcher = WebSearcher()
    results = await searcher.search_web(query, max_results)
    return searcher.format_search_results(results)


# Test function
async def test_search():
    """Test the web search functionality."""
    searcher = WebSearcher()
    results = await searcher.search_web("latest medical aesthetic treatments 2024")
    print(searcher.format_search_results(results))


if __name__ == "__main__":
    asyncio.run(test_search())