
import google.generativeai as genai
import os
import json
from prompts import SYSTEM_PROMPT

class GeminiService:
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Missing Gemini API key")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def check_connection(self):
        try:
            # A simple way to check the connection is to list the available models.
            models = [m for m in genai.list_models()]
            if any('generateContent' in m.supported_generation_methods for m in models):
                return {"status": "ok", "message": "Gemini API connection successful"}
            else:
                return {"status": "error", "message": "No suitable Gemini models found"}
        except Exception as e:
            return {"status": "error", "message": f"Error connecting to Gemini API: {e}"}

    def generate_slides(self, video_analysis: dict, user_query: str) -> dict:
        try:
            prompt = SYSTEM_PROMPT.format(
                video_analysis=video_analysis,
                user_query=user_query
            )
            response = self.model.generate_content(prompt)
            
            text = response.text
            
            # Find the start and end of the JSON object
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start == -1 or end == 0:
                return {"error": "No JSON object found in Gemini response", "raw_response": text}

            json_text = text[start:end]
            
            # Load the response as JSON
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            return {"error": f"Failed to decode Gemini response as JSON: {e}", "raw_response": text}
        except Exception as e:
            return {"error": f"An unexpected error occurred: {type(e).__name__} - {e}", "raw_response": getattr(response, 'text', 'N/A')}
