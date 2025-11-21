from agents.agent_base import BaseAgent

def create_editing_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="EditingAgent",
        model_name=model_name,
        tools=[],
        system_instruction=(
            "You are an Editor. Your goal is to polish the draft. "
            "1. Fix grammar and clarity. "
            "2. formatting: Ensure Markdown headers and code blocks are correct. "
            "3. Check the 'preferences' in the input: "
            "   - Does the tone match? If not, rewrite sections to match. "
            "   - Is the length sufficient? If too short, expand the conclusion. "
            "4. Add a short, professional author's note at the very end. "
            "Return the final polished blog post."
        )
    )