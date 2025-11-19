def create_outline_tool(key_points: list[str]):
    """Generates a blog outline structure based on provided key points."""
    print(f"[Tool] Creating outline for points: {key_points}")
    # Mock return
    return {
        "outline": {
            "title": "The Rise of AI Agents",
            "sections": [
                {"heading": "Introduction", "short_description": "What are agents?"},
                {"heading": "Core Concepts", "short_description": "Tools and planning."},
                {"heading": "Conclusion", "short_description": "Future outlook."}
            ]
        }
    }