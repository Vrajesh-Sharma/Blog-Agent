from agents.agent_base import BaseAgent

def create_writing_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="WritingAgent", # <--- Name added
        model_name=model_name,
        tools=[],
        system_instruction=(
            "You are a Writing Agent. Draft a complete technical blog using the outline. "
            "Return plain text markdown."
        )
    )