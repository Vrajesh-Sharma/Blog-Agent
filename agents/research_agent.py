from agents.agent_base import BaseAgent
from tools.google_search_tool import google_search_tool

def create_research_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="ResearchAgent",
        model_name=model_name,
        tools=[google_search_tool],
        response_mime_type="application/json",
        system_instruction=(
            "You are a Research Agent. Your goal is to research technical topics. "
            "CRITICAL RULE: Perform a MAXIMUM of 2 broad search queries to gather context. "
            "Do not waste quota on minor details. "
            "After searching, extract 3-5 key points and sources. "
            "Return strictly a JSON object with keys: 'key_points' (array) and 'sources' (array)."
        )
    )