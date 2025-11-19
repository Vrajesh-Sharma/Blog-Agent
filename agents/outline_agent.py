from agents.agent_base import BaseAgent
from tools.create_outline_tool import create_outline_tool

def create_outline_agent(model_name, tool_registry=None):
    return BaseAgent(
        model_name=model_name,
        tools=[create_outline_tool],
        response_mime_type="application/json",
        system_instruction=(
            "You are an Outline Agent. Create a structured blog outline. "
            "Return strictly a JSON object with keys: 'title' (string) and 'sections' (array of {heading, short_description})."
        )
    )