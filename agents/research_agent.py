from agents.agent_base import BaseAgent
from tools.google_search_tool import google_search_tool

def create_research_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="ResearchAgent", # <--- Name added
        model_name=model_name,
        tools=[google_search_tool],
        response_mime_type="application/json",
        system_instruction=(
            "You are a Research Agent. Research technical topics and extract 3-5 key points plus sources. "
            "Return strictly a JSON object with keys: 'key_points' (array) and 'sources' (array)."
        )
    )