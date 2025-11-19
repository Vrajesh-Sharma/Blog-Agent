from duckduckgo_search import DDGS

def google_search_tool(query: str):
    """
    Searches the web using DuckDuckGo and returns a list of relevant results.
    
    Args:
        query (str): The search query (e.g., "latest AI agent frameworks").
    """
    print(f"    🛠️  [Tool:GoogleSearch] Real Search for: '{query}'")
    
    try:
        # Perform the search (limit to 5 results to keep context small)
        results = DDGS().text(keywords=query, max_results=5)
        
        # Format the results into a clean list for the LLM
        clean_results = []
        for result in results:
            clean_results.append({
                "title": result.get('title'),
                "url": result.get('href'),
                "snippet": result.get('body')
            })
            
        return {"results": clean_results}

    except Exception as e:
        print(f"    ❌ [Tool:GoogleSearch] Failed: {e}")
        return {"error": "Search failed", "details": str(e)}