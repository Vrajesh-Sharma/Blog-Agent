# agents/agent_base.py
import google.generativeai as genai
import json

class BaseAgent:
    def __init__(self, model_name, system_instruction, tools=None, response_mime_type=None):
        self.model_name = model_name
        # Configure the model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction,
            tools=tools
        )
        self.generation_config = {}
        
        # If the agent must return JSON (like Research/Outline), we force it here
        if response_mime_type:
            self.generation_config["response_mime_type"] = response_mime_type

    def act(self, inputs, session_ref=None, memory_ref=None):
        """
        Executes the agent's task. 
        Accepts session/memory refs to maintain compatibility with app.py, 
        but primarily uses 'inputs' for context.
        """
        # Convert the input dictionary to a prompt string
        prompt = f"Task Context: {json.dumps(inputs, default=str)}"

        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Return text directly
            result = response.text
            
            # If we expect JSON, try to parse it to ensure it's valid dict for the app
            if self.generation_config.get("response_mime_type") == "application/json":
                return json.loads(result)
            
            return result

        except Exception as e:
            print(f"Error in agent execution: {e}")
            return {"error": str(e)}