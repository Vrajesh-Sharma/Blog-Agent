from agents.agent_base import BaseAgent

def create_writing_agent(model_name, tool_registry=None):
    return BaseAgent(
        name="WritingAgent",
        model_name=model_name,
        tools=[],
        system_instruction=(
            "You are a generic Writing Agent. Draft a complete technical blog using the outline. "
            "INPUT DATA: You will receive a 'preferences' dictionary. You MUST strictly adhere to it: "
            "1. **Tone**: match the requested tone (e.g., Professional, Casual, Humorous). "
            "2. **Audience**: Write specifically for the target group (e.g., simplify for Beginners, deep dive for Developers). "
            "3. **Word Count**: The 'length' parameter is a MINIMUM requirement. Expand on points to meet it. "
            "4. **Code Snippets**: Check 'include_examples'. "
            "   - If TRUE: You MUST include code blocks (Python/JS/Pseudo) to illustrate technical concepts. "
            "   - If FALSE: Do NOT include any code blocks, use analogies instead. "
            "Return the blog in Markdown format."
        )
    )