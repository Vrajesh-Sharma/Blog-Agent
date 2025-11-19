from agents.agent_base import BaseAgent
from tools.google_search_tool import google_search_tool

def create_research_agent(model_name, tool_registry=None):
    return BaseAgent(
        model_name=model_name,
        tools=[google_search_tool], # Pass the function directly
        response_mime_type="application/json", # Force JSON output
        system_instruction=(
            "You are a Research Agent. Your goal is to research technical topics. "
            "Use the google_search_tool if necessary. "
            "Extract 3-5 key points and sources. "
            "Return strictly a JSON object with keys: 'key_points' (array of strings) and 'sources' (array of objects)."
        )
    )