from agents.agent_base import BaseAgent
from tools.create_outline_tool import create_outline_tool

def create_outline_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="OutlineAgent",
        model_name=model_name,
        tools=[create_outline_tool],
        response_mime_type="application/json",
        system_instruction=(
            "You are an Outline Agent. "
            "Your job is to create a blog structure based on research and user preferences. "
            "INPUT DATA: You will receive 'preferences' containing 'audience' and 'length'. "
            "CRITICAL: Adjust the depth of the outline based on the 'length' parameter. "
            " - If 'Short (500+)', create 3-4 main sections. "
            " - If 'Medium (750+)', create 5-6 sections. "
            " - If 'Long (1000+)', create 7+ detailed sections to ensure the writer can reach the word count. "
            "Return strictly a JSON object with keys: 'title' and 'sections'."
        )
    )