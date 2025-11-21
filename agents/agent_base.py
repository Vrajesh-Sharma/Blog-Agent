# agents/agent_base.py
import google.generativeai as genai
import json
import time
import random

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
        Executes the agent's task with Automatic Retry Logic for Rate Limits.
        """
        print(f"\n🤖 [{self.name}] ACTIVATED")
        
        # Convert the input dictionary to a prompt string
        prompt = f"Task Context: {json.dumps(inputs, default=str)}"
        print(f"    └─ Input Context: {str(inputs)[:100]}...")

        # --- RETRY LOGIC ---
        max_retries = 3
        base_delay = 15 # Start with 15 seconds wait if error occurs

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"    └─ Attempt {attempt + 1} of {max_retries}...")

                print(f"    └─ Processing (Tools Enabled)...")
                
                # Start chat with auto-function calling
                chat = self.model.start_chat(enable_automatic_function_calling=True)
                
                response = chat.send_message(
                    prompt,
                    generation_config=self.generation_config
                )
                
                result = response.text
                
                # Log success
                preview = str(result).replace('\n', ' ')[:80]
                print(f"✅ [{self.name}] COMPLETED. Result: {preview}...")

                # Manual JSON Parsing
                if "{" in result and "}" in result:
                    try:
                        start = result.find("{")
                        end = result.rfind("}") + 1
                        json_str = result[start:end]
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        pass # Fallback to returning text
                
                return result

            except Exception as e:
                error_str = str(e)
                # Check for Rate Limit (429) or Quota errors
                if "429" in error_str or "Quota exceeded" in error_str:
                    wait_time = base_delay * (2 ** attempt) + random.uniform(1, 5)
                    print(f"    ⚠️ [{self.name}] Rate Limit Hit! Cooling down for {wait_time:.1f}s...")
                    time.sleep(wait_time)
                    # Loop continues to next attempt...
                else:
                    # Real error (not rate limit) -> Crash immediately
                    print(f"❌ [{self.name}] ERROR: {e}")
                    return {"error": str(e)}
        
        # If loop finishes without success
        return {"error": "Operation failed after max retries due to Rate Limits."}