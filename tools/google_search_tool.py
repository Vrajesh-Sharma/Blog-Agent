def google_search_tool(query: str):
    """Searches Google for the query and returns a list of results."""
    print(f"[Tool] Searching Google for: {query}")
    # Mock return for now - Replace with SerpApi or Google Custom Search API later
    return {
        "results": [
            {"title": "Understanding Agentic AI", "url": "https://example.com/agentic-ai"},
            {"title": "AI Agents for Beginners", "url": "https://example.com/ai-agents"},
            {"title": "The Future of LLMs", "url": "https://example.com/future-llms"}
        ]
    }