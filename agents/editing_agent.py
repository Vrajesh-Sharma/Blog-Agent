from agents.agent_base import BaseAgent

def create_editing_agent(model_name, tool_registry=None):
    return BaseAgent(
        model_name=model_name,
        tools=[],
        system_instruction=(
            "You are an Editor. Polish the draft for grammar, clarity, and tone. "
            "Add an author's note at the end. Return the full final blog post in markdown."
        )
    )