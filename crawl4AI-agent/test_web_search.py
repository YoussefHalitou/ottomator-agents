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
        from ai_manager import test_clinic_query_logic
        
        # Test queries
        test_queries = [
            "What studies exist on Botox?",
            "Show me research on dermal fillers", 
            "Tell me about Dr. Larisa Pfahl",
            "Clinical trials for laser treatments"
        ]
        
        async def run_tests():
            for query in test_queries:
                result = await test_clinic_query_logic(query)
                needs_search = result["needs_web_search"]
                keywords = result["decision_keywords"]
                
                print(f"🔍 '{query}'")
                print(f"   → Web search needed: {'✅ YES' if needs_search else '❌ NO'}")
                print(f"   → Keywords found: {keywords}")
                print(f"   → RAG response: {result['rag_response'][:100]}...")
                if result['web_search_query']:
                    print(f"   → Web query: {result['web_search_query']}")
                print()
        
        asyncio.run(run_tests())
        return True
        
    except Exception as e:
        print(f"❌ AI Manager test failed: {e}")
        return False

def test_search_query_optimization():
    """Test search query optimization"""
    print("\n🧪 Testing Search Query Optimization...")
    
    try:
        from ai_manager import test_clinic_query_logic
        
        test_queries = [
            "What studies exist on Botox?",
            "Latest research on dermal fillers",
            "Clinical trials for laser treatments",
            "Show me evidence for Morpheus8"
        ]
        
        async def run_optimization_tests():
            for query in test_queries:
                result = await test_clinic_query_logic(query)
                if result['web_search_query']:
                    print(f"🎯 '{query}'")
                    print(f"   → Optimized: '{result['web_search_query']}'")
                    print(f"   → Decision: {'Web search needed' if result['needs_web_search'] else 'RAG sufficient'}")
                    print()
        
        asyncio.run(run_optimization_tests())
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