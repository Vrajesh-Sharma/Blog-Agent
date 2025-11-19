from agents.agent_base import BaseAgent

def create_editing_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="EditingAgent", # <--- Name added
        model_name=model_name,
        tools=[],
        system_instruction=(
            "You are an Editor. Polish the draft for grammar and clarity. "
            "Return the final blog post."
        )
    )