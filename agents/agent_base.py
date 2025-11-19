# agents/agent_base.py
import google.generativeai as genai
import json

class BaseAgent:
    def __init__(self, name, model_name, system_instruction, tools=None, response_mime_type=None):
        self.name = name
        self.model_name = model_name
        print(f"   [System] Initializing Agent: {self.name} ({model_name})")
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            tools=tools
        )
        self.generation_config = {}
        
        # Only enforce JSON if NO tools are present to prevent API conflicts
        if response_mime_type and not tools:
            self.generation_config["response_mime_type"] = response_mime_type

    def act(self, inputs, session_ref=None, memory_ref=None):
        """
        Executes the agent's task using a Chat Session to enable automatic tool use.
        """
        print(f"\n🤖 [{self.name}] ACTIVATED")
        
        # Convert the input dictionary to a prompt string
        prompt = f"Task Context: {json.dumps(inputs, default=str)}"
        print(f"    └─ Input Context: {str(inputs)[:100]}...")

        try:
            print(f"    └─ Processing (Tools Enabled)...")
            
            # --- THE FIX IS HERE ---
            # We start a chat session with automatic function calling enabled.
            # This allows the SDK to execute the tools (like google_search) 
            # automatically when the model asks for them.
            chat = self.model.start_chat(enable_automatic_function_calling=True)
            
            response = chat.send_message(
                prompt,
                generation_config=self.generation_config
            )
            
            # Get the final text result after tools have run
            result = response.text
            
            # Log success
            preview = str(result).replace('\n', ' ')[:80]
            print(f"✅ [{self.name}] COMPLETED. Result: {preview}...")

            # specific logic for Research/Outline to ensure the app gets the Dict it expects
            # (Since we disabled strict JSON mode for agents with tools, we try to parse manually)
            if "{" in result and "}" in result:
                try:
                    # Find the first '{' and last '}' to extract JSON if there's extra text
                    start = result.find("{")
                    end = result.rfind("}") + 1
                    json_str = result[start:end]
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass # Fallback to returning text if parsing fails
            
            return result

        except Exception as e:
            print(f"❌ [{self.name}] ERROR: {e}")
            # Return a structured error so the frontend doesn't just break silently
            return {"error": str(e)}