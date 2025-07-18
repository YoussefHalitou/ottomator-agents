#!/usr/bin/env python3
"""
Simple test to verify web search functionality
"""

import asyncio
import sys
import os

def test_web_search_direct():
    """Test web search module directly"""
    print("🧪 Testing Web Search Module Directly...")
    
    try:
        # Import the web search module
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from web_search import WebSearcher
        
        async def run_search():
            searcher = WebSearcher()
            
            # Test search for studies
            print("🔍 Searching for: 'Botox effectiveness clinical studies'")
            results = await searcher.search_web("Botox effectiveness clinical studies", max_results=3)
            
            print(f"📊 Found {len(results)} results")
            
            for i, result in enumerate(results, 1):
                print(f"\n📄 Result {i}:")
                print(f"  Title: {result.get('title', 'No title')}")
                print(f"  URL: {result.get('url', 'No URL')}")
                print(f"  Content: {result.get('content', 'No content')[:100]}...")
            
            # Test formatted output
            formatted = searcher.format_search_results(results)
            print("\n" + "="*50)
            print("📝 FORMATTED OUTPUT:")
            print("="*50)
            print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
        asyncio.run(run_search())
        return True
        
    except Exception as e:
        print(f"❌ Web search test failed: {e}")
        return False

def test_ai_manager_keywords():
    """Test if AI Manager detects study keywords"""
    print("\n🧪 Testing AI Manager Keyword Detection...")
    
    try:
        from ai_manager import AIManager
        
        manager = AIManager()
        
        # Test queries
        test_queries = [
            "What studies exist on Botox?",
            "Show me research on dermal fillers", 
            "Tell me about Dr. Larisa Pfahl",
            "Clinical trials for laser treatments"
        ]
        
        for query in test_queries:
            # Create a mock RAG response
            mock_rag_response = {
                'response': "I don't have current information about this topic.",
                'complete': False
            }
            
            needs_search = manager._analyze_need_for_web_search(query, mock_rag_response['response'])
            print(f"🔍 '{query}' → Web search needed: {'✅ YES' if needs_search else '❌ NO'}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Manager test failed: {e}")
        return False

def test_search_query_optimization():
    """Test search query optimization"""
    print("\n🧪 Testing Search Query Optimization...")
    
    try:
        from ai_manager import AIManager
        
        manager = AIManager()
        
        test_queries = [
            "What studies exist on Botox?",
            "Latest research on dermal fillers",
            "Clinical trials for laser treatments",
            "Show me evidence for Morpheus8"
        ]
        
        for query in test_queries:
            optimized = manager._create_web_search_query(query, "mock rag response")
            print(f"🎯 '{query}'")
            print(f"   → Optimized: '{optimized}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Query optimization test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 WEB SEARCH FUNCTIONALITY TEST")
    print("="*50)
    
    tests = [
        ("Web Search Direct", test_web_search_direct),
        ("AI Manager Keywords", test_ai_manager_keywords), 
        ("Search Query Optimization", test_search_query_optimization)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Web search functionality is working!")
    else:
        print("⚠️ Some web search components have issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)