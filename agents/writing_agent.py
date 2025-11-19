from agents.agent_base import BaseAgent

def create_writing_agent(model_name, tool_registry=None):
    return BaseAgent(
        model_name=model_name,
        tools=[], # No tools needed for writing usually
        system_instruction=(
            "You are a generic Writing Agent. Draft a complete technical blog using the provided outline and key points. "
            "Include examples and code snippets where relevant. Return plain text markdown."
        )
    )