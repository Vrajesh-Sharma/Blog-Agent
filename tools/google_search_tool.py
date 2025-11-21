from ddgs import DDGS

def google_search_tool(query: str):
    """
    Searches the web using DuckDuckGo and returns a list of relevant results.
    """
    print(f"    🛠️  [Tool:GoogleSearch] Real Search for: '{query}'")

    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)

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
